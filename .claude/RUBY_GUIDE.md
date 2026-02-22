# Ruby Development Guide

**Version**: 1.0
**Last Updated**: {{CURRENT_DATE}}

---

## Overview

This guide outlines Ruby coding standards, best practices, and patterns for {{PROJECT_NAME}}. All Ruby code must follow these guidelines to ensure consistency, maintainability, and quality.

---

## Code Style

### RuboCop Compliance

All Ruby code must pass [RuboCop](https://rubocop.org/) with no offenses.

**Enforced by**: RuboCop (with rubocop-rails, rubocop-rspec plugins)

```ruby
# Good: Idiomatic Ruby
# frozen_string_literal: true

def calculate_total_price(items, tax_rate: 0.08)
  subtotal = items.sum { |item| item[:price] * item[:quantity] }
  subtotal * (1 + tax_rate)
end

# Bad: Not idiomatic
def calculateTotalPrice(items,taxRate=0.08)
  subtotal = 0
  items.each { |item| subtotal = subtotal + item[:price] * item[:quantity] }
  return subtotal * (1 + taxRate)
end
```

### Frozen String Literals

Add `# frozen_string_literal: true` at the top of every Ruby file to prevent accidental string mutation and improve performance.

```ruby
# frozen_string_literal: true

class UserService
  # ...
end
```

### Naming Conventions

- **Methods and variables**: `snake_case`
- **Classes and modules**: `CamelCase`
- **Constants**: `SCREAMING_SNAKE_CASE`
- **Predicates**: end with `?` (e.g., `valid?`, `admin?`)
- **Dangerous methods**: end with `!` (e.g., `save!`, `update!`)

---

## Dependency Management

### Bundler and Gemfile

Use Bundler to manage dependencies. Pin major versions.

```ruby
# Gemfile
source 'https://rubygems.org'

ruby '3.3.0'

gem 'rails', '~> 7.1'
gem 'pg', '~> 1.5'
gem 'puma', '~> 6.4'

group :development, :test do
  gem 'rspec-rails', '~> 6.1'
  gem 'factory_bot_rails', '~> 6.4'
  gem 'rubocop', '~> 1.60', require: false
  gem 'rubocop-rails', require: false
  gem 'rubocop-rspec', require: false
end

group :test do
  gem 'simplecov', require: false
  gem 'vcr', '~> 6.2'
  gem 'webmock', '~> 3.23'
  gem 'timecop', '~> 0.9'
  gem 'shoulda-matchers', '~> 6.0'
  gem 'database_cleaner-active_record', '~> 2.1'
end
```

---

## Rails MVC Patterns

### Controllers

Keep controllers thin — delegate business logic to service objects.

```ruby
# frozen_string_literal: true

class UsersController < ApplicationController
  before_action :authenticate_user!
  before_action :set_user, only: %i[show update destroy]

  def create
    result = UserCreationService.call(user_params)

    if result.success?
      render json: UserSerializer.new(result.user), status: :created
    else
      render json: { errors: result.errors }, status: :unprocessable_entity
    end
  end

  private

  def set_user
    @user = User.find(params[:id])
  end

  def user_params
    params.require(:user).permit(:email, :name, :password)
  end
end
```

### Service Objects

Encapsulate business logic in service objects.

```ruby
# frozen_string_literal: true

class UserCreationService
  Result = Struct.new(:success?, :user, :errors, keyword_init: true)

  def self.call(attributes)
    new(attributes).call
  end

  def initialize(attributes)
    @attributes = attributes
  end

  def call
    user = User.new(@attributes)

    if user.save
      UserMailer.welcome(user).deliver_later
      Result.new(success?: true, user: user, errors: [])
    else
      Result.new(success?: false, user: nil, errors: user.errors.full_messages)
    end
  end
end
```

### Models

Keep models focused on data validation and associations.

```ruby
# frozen_string_literal: true

class User < ApplicationRecord
  # Associations
  has_many :posts, dependent: :destroy
  belongs_to :organization

  # Validations
  validates :email, presence: true, uniqueness: { case_sensitive: false },
                    format: { with: URI::MailTo::EMAIL_REGEXP }
  validates :name, presence: true, length: { minimum: 2, maximum: 100 }

  # Scopes
  scope :active, -> { where(active: true) }
  scope :admins, -> { where(role: :admin) }

  # Enums
  enum role: { member: 0, admin: 1, superadmin: 2 }

  # Callbacks (use sparingly)
  before_validation :normalize_email

  private

  def normalize_email
    self.email = email&.downcase&.strip
  end
end
```

---

## ActiveRecord

### Avoid N+1 Queries

Use `includes` or `eager_load` for associations.

```ruby
# Good: Eager loading
users = User.includes(:posts, :organization).active

# Bad: N+1 query problem
users = User.active
users.each do |user|
  puts user.posts.count  # triggers N additional queries!
end
```

### Scopes and Queries

```ruby
# Good: Scoped queries
User.active.admins.order(created_at: :desc).limit(10)

# Good: Find in batches for large datasets
User.find_each(batch_size: 500) do |user|
  UserDataExportJob.perform_later(user.id)
end
```

### Migrations

Always write reversible migrations.

```ruby
class AddStatusToUsers < ActiveRecord::Migration[7.1]
  def change
    add_column :users, :status, :string, null: false, default: 'active'
    add_index :users, :status
  end
end
```

---

## Error Handling

### Explicit Error Handling

Always handle expected errors explicitly with specific rescue clauses.

```ruby
# frozen_string_literal: true

class UserService
  def find!(id)
    User.find(id)
  rescue ActiveRecord::RecordNotFound
    raise UserNotFoundError, "User #{id} not found"
  end

  def create!(attributes)
    User.create!(attributes)
  rescue ActiveRecord::RecordInvalid => e
    raise ValidationError, e.message
  rescue ActiveRecord::RecordNotUnique
    raise DuplicateUserError, 'User with this email already exists'
  end
end
```

### Custom Exception Classes

Create custom exceptions for domain-specific errors.

```ruby
# frozen_string_literal: true

module Errors
  class BaseError < StandardError; end
  class UserNotFoundError < BaseError; end
  class DuplicateUserError < BaseError; end
  class ValidationError < BaseError; end
  class AuthorizationError < BaseError; end
end
```

---

## Testing

### RSpec Best Practices

```ruby
# frozen_string_literal: true

require 'rails_helper'

RSpec.describe UsersController, type: :request do
  describe 'POST /users' do
    context 'with valid parameters' do
      let(:valid_params) do
        { user: { email: 'test@example.com', name: 'Test User', password: 'SecurePass123!' } }
      end

      it 'creates a user and returns 201' do
        post '/users', params: valid_params, as: :json

        expect(response).to have_http_status(:created)
        expect(JSON.parse(response.body)['email']).to eq('test@example.com')
      end
    end

    context 'with duplicate email' do
      let!(:existing_user) { create(:user, email: 'test@example.com') }

      it 'returns 422 with error message' do
        post '/users', params: { user: { email: 'test@example.com', name: 'Other' } }, as: :json

        expect(response).to have_http_status(:unprocessable_entity)
        expect(JSON.parse(response.body)['errors']).to include(match(/email/i))
      end
    end
  end
end
```

---

## Security

### Strong Parameters

Always use strong parameters in Rails controllers.

```ruby
def user_params
  params.require(:user).permit(:email, :name, :password, :role)
end
```

### SQL Injection Prevention

Always use ActiveRecord finders or parameterized queries.

```ruby
# Good: Safe parameterized query
User.where('email = ?', params[:email])
User.where(email: params[:email])

# Bad: SQL injection risk!
User.where("email = '#{params[:email]}'")  # NEVER DO THIS!
```

### Mass Assignment

Never allow blanket attribute assignment.

```ruby
# Good: Explicit permit
params.require(:user).permit(:email, :name)

# Bad: Allows all attributes (mass assignment vulnerability)
User.new(params[:user])  # without strong parameters
```

---

## Tools Configuration

### .rubocop.yml

```yaml
require:
  - rubocop-rails
  - rubocop-rspec

AllCops:
  NewCops: enable
  TargetRubyVersion: 3.3
  Exclude:
    - 'db/schema.rb'
    - 'db/migrate/**/*'
    - 'vendor/**/*'
    - 'bin/**/*'
    - 'node_modules/**/*'

Style/FrozenStringLiteralComment:
  Enabled: true
  EnforcedStyle: always

Metrics/MethodLength:
  Max: 15

Metrics/ClassLength:
  Max: 200

Metrics/BlockLength:
  Exclude:
    - 'spec/**/*'
    - 'config/routes.rb'

Layout/LineLength:
  Max: 120
```

### SimpleCov Configuration

Add to `spec/spec_helper.rb`:

```ruby
require 'simplecov'
SimpleCov.start 'rails' do
  add_filter '/spec/'
  add_filter '/config/'
  add_filter '/vendor/'
  minimum_coverage 80
end
```

---

## Resources

- [Ruby Style Guide](https://rubystyle.guide/) - Community Ruby style guide
- [Rails Guides](https://guides.rubyonrails.org/) - Official Rails documentation
- [RuboCop Documentation](https://docs.rubocop.org/) - Linter configuration
- [RSpec Documentation](https://rspec.info/) - Testing framework
- [FactoryBot Documentation](https://github.com/thoughtbot/factory_bot) - Test factories
- [SimpleCov](https://github.com/simplecov-ruby/simplecov) - Code coverage

---

**Last Updated**: {{CURRENT_DATE}}
