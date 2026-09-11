-- ============================================
-- BUSINESS / ORGANIZATIONAL STRUCTURE
-- ============================================

CREATE TABLE business (
    business_id         SERIAL PRIMARY KEY,
    name                VARCHAR(150) NOT NULL,
    registration_number VARCHAR(50) UNIQUE NOT NULL,
    contact_email       VARCHAR(150)
);

CREATE TABLE branch (
    branch_id   SERIAL PRIMARY KEY,
    business_id INTEGER NOT NULL REFERENCES business(business_id) ON DELETE CASCADE,
    name        VARCHAR(150) NOT NULL,
    address     VARCHAR(255)
);

-- ============================================
-- ADMIN / APPROVAL
-- ============================================

CREATE TABLE admin (
    admin_id   SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name  VARCHAR(100) NOT NULL,
    email      VARCHAR(150) UNIQUE NOT NULL,
    password   VARCHAR(255) NOT NULL
);

CREATE TABLE approval_log (
    approval_log_id SERIAL PRIMARY KEY,
    admin_id        INTEGER NOT NULL REFERENCES admin(admin_id) ON DELETE CASCADE,
    entity_type     VARCHAR(50) NOT NULL,
    entity_id       INTEGER NOT NULL,
    action          VARCHAR(50) NOT NULL,
    comments        TEXT,
    action_date     TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ============================================
-- DIETITIAN
-- ============================================

CREATE TABLE dietitian (
    dietitian_id        SERIAL PRIMARY KEY,
    branch_id           INTEGER NOT NULL REFERENCES branch(branch_id) ON DELETE CASCADE,
    first_name          VARCHAR(100) NOT NULL,
    last_name           VARCHAR(100) NOT NULL,
    email               VARCHAR(150) UNIQUE NOT NULL,
    password            VARCHAR(255) NOT NULL,
    registration_number VARCHAR(50) UNIQUE NOT NULL,
    specialisation      VARCHAR(150),
    status              VARCHAR(20) NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED', 'SUSPENDED'))
);

-- ============================================
-- CLIENT
-- ============================================

CREATE TABLE client (
    client_id           SERIAL PRIMARY KEY,
    dietitian_id        INTEGER REFERENCES dietitian(dietitian_id) ON DELETE SET NULL,
    name                VARCHAR(150) NOT NULL,
    email               VARCHAR(150) UNIQUE NOT NULL,
    password            VARCHAR(255) NOT NULL,
    date_of_birth       DATE NOT NULL,
    gender              VARCHAR(20),
    height              NUMERIC(5,2),
    activity_level      VARCHAR(30),
    dietary_preferences TEXT,
    allergies           TEXT,
    status              VARCHAR(20) NOT NULL DEFAULT 'ACTIVE'
        CHECK (status IN ('ACTIVE', 'INACTIVE', 'SUSPENDED'))
);

-- ============================================
-- APPOINTMENT
-- ============================================

CREATE TABLE appointment (
    appointment_id SERIAL PRIMARY KEY,
    client_id      INTEGER NOT NULL REFERENCES client(client_id) ON DELETE CASCADE,
    dietitian_id   INTEGER NOT NULL REFERENCES dietitian(dietitian_id) ON DELETE CASCADE,
    branch_id      INTEGER NOT NULL REFERENCES branch(branch_id) ON DELETE CASCADE,
    date_time      TIMESTAMP NOT NULL,
    duration       INTEGER NOT NULL,
    status         VARCHAR(20) NOT NULL DEFAULT 'SCHEDULED'
        CHECK (status IN ('SCHEDULED', 'COMPLETED', 'CANCELLED', 'NO_SHOW')),
    notes          TEXT
);

-- ============================================
-- NUTRITION GOAL
-- ============================================

CREATE TABLE nutrition_goal (
    goal_id       SERIAL PRIMARY KEY,
    client_id     INTEGER NOT NULL REFERENCES client(client_id) ON DELETE CASCADE,
    goal_type     VARCHAR(100) NOT NULL,
    current_value NUMERIC(6,2),
    target_value  NUMERIC(6,2),
    target_date   DATE
);

-- ============================================
-- AI RECOMMENDATION
-- ============================================

CREATE TABLE ai_recommendation (
    recommendation_id SERIAL PRIMARY KEY,
    client_id         INTEGER NOT NULL REFERENCES client(client_id) ON DELETE CASCADE,
    generated_date    TIMESTAMP NOT NULL DEFAULT NOW(),
    recommendation_text TEXT NOT NULL
);

-- ============================================
-- PROGRESS LOG
-- ============================================

CREATE TABLE progress_log (
    progress_log_id SERIAL PRIMARY KEY,
    client_id       INTEGER NOT NULL REFERENCES client(client_id) ON DELETE CASCADE,
    log_date        DATE NOT NULL,
    weight          NUMERIC(5,2),
    body_fat_pct    NUMERIC(4,2),
    waist_cm        NUMERIC(5,2),
    notes           TEXT
);

-- ============================================
-- MEAL PLAN
-- ============================================

CREATE TABLE meal_plan (
    meal_plan_id    SERIAL PRIMARY KEY,
    client_id       INTEGER NOT NULL REFERENCES client(client_id) ON DELETE CASCADE,
    dietitian_id    INTEGER NOT NULL REFERENCES dietitian(dietitian_id) ON DELETE CASCADE,
    target_calories INTEGER,
    start_date      DATE NOT NULL,
    end_date        DATE,
    CHECK (end_date IS NULL OR end_date >= start_date)
);

-- ============================================
-- FOOD ITEM
-- ============================================

CREATE TABLE food_item (
    food_item_id SERIAL PRIMARY KEY,
    name         VARCHAR(150) NOT NULL,
    calories     NUMERIC(6,2) NOT NULL,
    protein      NUMERIC(6,2),
    carbs        NUMERIC(6,2),
    fat          NUMERIC(6,2)
);

-- ============================================
-- MEAL PLAN ITEM
-- ============================================

CREATE TABLE meal_plan_item (
    meal_plan_item_id SERIAL PRIMARY KEY,
    meal_plan_id      INTEGER NOT NULL REFERENCES meal_plan(meal_plan_id) ON DELETE CASCADE,
    food_item_id      INTEGER NOT NULL REFERENCES food_item(food_item_id) ON DELETE RESTRICT,
    meal_type         VARCHAR(20) NOT NULL
        CHECK (meal_type IN ('BREAKFAST', 'LUNCH', 'DINNER', 'SNACK')),
    portion           NUMERIC(6,2) NOT NULL
);

-- ============================================
-- INDEXES
-- ============================================

CREATE INDEX idx_branch_business ON branch(business_id);
CREATE INDEX idx_dietitian_branch ON dietitian(branch_id);
CREATE INDEX idx_client_dietitian ON client(dietitian_id);
CREATE INDEX idx_appointment_client ON appointment(client_id);
CREATE INDEX idx_appointment_dietitian ON appointment(dietitian_id);
CREATE INDEX idx_appointment_branch ON appointment(branch_id);
CREATE INDEX idx_nutrition_goal_client ON nutrition_goal(client_id);
CREATE INDEX idx_ai_recommendation_client ON ai_recommendation(client_id);
CREATE INDEX idx_progress_log_client ON progress_log(client_id);
CREATE INDEX idx_meal_plan_client ON meal_plan(client_id);
CREATE INDEX idx_meal_plan_dietitian ON meal_plan(dietitian_id);
CREATE INDEX idx_meal_plan_item_plan ON meal_plan_item(meal_plan_id);
CREATE INDEX idx_meal_plan_item_food ON meal_plan_item(food_item_id);
CREATE INDEX idx_approval_log_admin ON approval_log(admin_id);
