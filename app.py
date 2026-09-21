from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import uuid

app = FastAPI(
    title="Dietitian & Nutrition Management System",
    description="Full Implementation: Sections 1 through 6 REST API Specification",
    version="1.0.0",
    docs_url="/"  # Configures Swagger UI to load on the root URL
)

# --- IN-MEMORY DATABASE MOCKS ---
users_db: Dict[str, dict] = {}
clients_db: Dict[str, dict] = {}
appointments_db: Dict[str, dict] = {}
meal_plans_db: Dict[str, dict] = {}
ai_recommendations_db: Dict[str, dict] = {}
foods_db: List[dict] = [
    {"food_id": "f1", "name": "Oatmeal", "calories": 150, "protein_g": 5.0, "carbs_g": 27.0, "fat_g": 3.0, "glycemic_index": 55},
    {"food_id": "f2", "name": "Grilled Chicken Breast", "calories": 165, "protein_g": 31.0, "carbs_g": 0.0, "fat_g": 3.6, "glycemic_index": 0}
]

# --- PYDANTIC SCHEMAS ---

# Section 1 Schemas
class DietitianRegister(BaseModel):
    full_name: str
    email: str
    license_number: str

class ClientRegister(BaseModel):
    full_name: str
    email: str
    dietitian_id: str

class LoginRequest(BaseModel):
    email: str
    password: str

class AdminApproval(BaseModel):
    dietitian_id: str
    status: str  # APPROVED, REJECTED, SUSPENDED

class BranchCreate(BaseModel):
    name: str
    address: str

# Section 2 Schemas
class PregnancyLog(BaseModel):
    trimester: int = Field(..., ge=1, le=3)
    due_date: str

class LactationLog(BaseModel):
    is_active: bool
    notes: Optional[str] = None

class AllergyEntry(BaseModel):
    allergen: str
    severity: str

class MedicalConditionEntry(BaseModel):
    condition_name: str
    icd_code: Optional[str] = None

# Section 3 Schemas
class MetricLog(BaseModel):
    metric_type: str  # HbA1c, Fasting Blood Glucose, BP
    value: str

class ProgressLog(BaseModel):
    weight_kg: float
    calories: int
    steps: int
    sleep_hours: float

# Section 4 Schemas
class AppointmentCreate(BaseModel):
    client_id: str
    dietitian_id: str
    appointment_date: str

class GoalCreate(BaseModel):
    client_id: str
    target_metric: str
    target_value: float

# Section 5 Schemas
class FoodItem(BaseModel):
    food_id: str
    name: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    glycemic_index: Optional[int] = None

class RecipeCreate(BaseModel):
    title: str
    ingredients: List[str]
    instructions: str

class MealPlanRequest(BaseModel):
    client_id: str
    diet_type: str
    days: int = Field(default=7, ge=1, le=30)

class MealPlanResponse(BaseModel):
    meal_plan_id: str
    client_id: str
    diet_type: str
    days: int
    meals: List[str]
    status: str = "GENERATED"

# Section 6 Schemas
class AIGenerateRequest(BaseModel):
    client_id: str
    dietary_goal: str

class RecommendationReview(BaseModel):
    action: str  # APPROVED, MODIFIED, REJECTED
    notes: Optional[str] = None


# --- ROUTE HANDLERS ---

# --- 1. AUTHENTICATION, ADMINISTRATION & PRACTICE SETUP ---

@app.post("/api/v1/auth/register/dietitian", tags=["1. Auth & Admin"])
def register_dietitian(data: DietitianRegister):
    user_id = f"diet_{uuid.uuid4().hex[:8]}"
    user = {"id": user_id, "type": "dietitian", "status": "PENDING", **data.model_dump()}
    users_db[user_id] = user
    return {"message": "Dietitian registered successfully", "user": user}

@app.post("/api/v1/auth/register/client", tags=["1. Auth & Admin"])
def register_client(data: ClientRegister):
    user_id = f"cli_{uuid.uuid4().hex[:8]}"
    user = {"id": user_id, "type": "client", **data.model_dump()}
    users_db[user_id] = user
    return {"message": "Client registered successfully", "user": user}

@app.post("/api/v1/auth/login", tags=["1. Auth & Admin"])
def login(data: LoginRequest):
    return {"access_token": f"mock_jwt_token_{uuid.uuid4().hex[:12]}", "token_type": "bearer"}

@app.post("/api/v1/admin/approvals", tags=["1. Auth & Admin"])
def review_dietitian(data: AdminApproval):
    if data.dietitian_id not in users_db:
        raise HTTPException(status_code=404, detail="Dietitian not found")
    users_db[data.dietitian_id]["status"] = data.status
    return {"message": f"Dietitian status updated to {data.status}"}

@app.post("/api/v1/branches", tags=["1. Auth & Admin"])
def create_branch(data: BranchCreate):
    return {"message": "Branch created successfully", "branch": data.model_dump()}


# --- 2. CLIENT HEALTH, LIFE STAGE & CLINICAL HISTORY ---

@app.get("/api/v1/clients/{client_id}/profile", tags=["2. Client Health & History"])
def get_client_profile(client_id: str):
    if client_id not in clients_db:
        clients_db[client_id] = {"allergies": [], "conditions": [], "metrics": [], "progress": []}
    return clients_db[client_id]

@app.post("/api/v1/clients/{client_id}/pregnancy", tags=["2. Client Health & History"])
def log_pregnancy(client_id: str, data: PregnancyLog):
    if client_id not in clients_db:
        clients_db[client_id] = {"allergies": [], "conditions": [], "metrics": [], "progress": []}
    clients_db[client_id]["pregnancy"] = data.model_dump()
    return {"message": "Pregnancy parameters updated", "data": clients_db[client_id]["pregnancy"]}

@app.post("/api/v1/clients/{client_id}/lactation", tags=["2. Client Health & History"])
def log_lactation(client_id: str, data: LactationLog):
    if client_id not in clients_db:
        clients_db[client_id] = {"allergies": [], "conditions": [], "metrics": [], "progress": []}
    clients_db[client_id]["lactation"] = data.model_dump()
    return {"message": "Lactation state updated", "data": clients_db[client_id]["lactation"]}

@app.post("/api/v1/clients/{client_id}/allergies", tags=["2. Client Health & History"])
def add_allergy(client_id: str, data: AllergyEntry):
    if client_id not in clients_db:
        clients_db[client_id] = {"allergies": [], "conditions": [], "metrics": [], "progress": []}
    clients_db[client_id]["allergies"].append(data.model_dump())
    return {"message": "Allergy mapped successfully", "allergies": clients_db[client_id]["allergies"]}

@app.post("/api/v1/clients/{client_id}/medical-conditions", tags=["2. Client Health & History"])
def add_medical_condition(client_id: str, data: MedicalConditionEntry):
    if client_id not in clients_db:
        clients_db[client_id] = {"allergies": [], "conditions": [], "metrics": [], "progress": []}
    clients_db[client_id]["conditions"].append(data.model_dump())
    return {"message": "Medical condition added", "conditions": clients_db[client_id]["conditions"]}


# --- 3. CLINICAL LABS & DAILY PROGRESS LOGS ---

@app.post("/api/v1/clients/{client_id}/metrics", tags=["3. Clinical Labs & Progress"])
def log_metric(client_id: str, data: MetricLog):
    if client_id not in clients_db:
        clients_db[client_id] = {"allergies": [], "conditions": [], "metrics": [], "progress": []}
    clients_db[client_id]["metrics"].append(data.model_dump())
    return {"message": "Metric logged successfully", "metrics": clients_db[client_id]["metrics"]}

@app.get("/api/v1/clients/{client_id}/metrics", tags=["3. Clinical Labs & Progress"])
def get_metrics(client_id: str):
    if client_id not in clients_db:
        raise HTTPException(status_code=404, detail="Client record not found")
    return clients_db[client_id].get("metrics", [])

@app.post("/api/v1/clients/{client_id}/progress", tags=["3. Clinical Labs & Progress"])
def log_progress(client_id: str, data: ProgressLog):
    if client_id not in clients_db:
        clients_db[client_id] = {"allergies": [], "conditions": [], "metrics": [], "progress": []}
    clients_db[client_id]["progress"].append(data.model_dump())
    return {"message": "Progress entry saved", "progress": clients_db[client_id]["progress"]}

@app.get("/api/v1/clients/{client_id}/progress", tags=["3. Clinical Labs & Progress"])
def get_progress(client_id: str):
    if client_id not in clients_db:
        raise HTTPException(status_code=404, detail="Client record not found")
    return clients_db[client_id].get("progress", [])


# --- 4. APPOINTMENTS & GOALS ---

@app.post("/api/v1/appointments", tags=["4. Appointments & Goals"])
def create_appointment(data: AppointmentCreate):
    appt_id = f"appt_{uuid.uuid4().hex[:8]}"
    appointment = {"appointment_id": appt_id, "status": "SCHEDULED", **data.model_dump()}
    appointments_db[appt_id] = appointment
    return {"message": "Appointment scheduled", "appointment": appointment}

@app.get("/api/v1/appointments", tags=["4. Appointments & Goals"])
def get_appointments():
    return list(appointments_db.values())

@app.post("/api/v1/goals", tags=["4. Appointments & Goals"])
def set_goal(data: GoalCreate):
    return {"message": "Target goal created successfully", "goal": data.model_dump()}


# --- 5. FOODS, RECIPES & MEAL PLANNING ---

@app.get("/api/v1/foods", response_model=List[FoodItem], tags=["5. Foods & Meal Planning"])
def get_foods():
    return foods_db

@app.post("/api/v1/recipes", tags=["5. Foods & Meal Planning"])
def create_recipe(data: RecipeCreate):
    recipe_id = f"rec_{uuid.uuid4().hex[:8]}"
    return {"message": "Recipe created", "recipe_id": recipe_id, "details": data.model_dump()}

@app.post("/api/v1/meal-plans", response_model=MealPlanResponse, status_code=status.HTTP_201_CREATED, tags=["5. Foods & Meal Planning"])
def create_meal_plan(request: MealPlanRequest):
    plan_id = f"plan_{uuid.uuid4().hex[:8]}"
    sample_meals = [
        f"Breakfast: Oatmeal with chia seeds ({request.diet_type})",
        f"Lunch: Quinoa bowl with grilled chicken",
        f"Dinner: Salmon with steamed broccoli"
    ]
    plan_data = {
        "meal_plan_id": plan_id,
        "client_id": request.client_id,
        "diet_type": request.diet_type,
        "days": request.days,
        "meals": sample_meals,
        "status": "GENERATED"
    }
    meal_plans_db[plan_id] = plan_data
    return plan_data

@app.get("/api/v1/meal-plans/{meal_plan_id}", response_model=MealPlanResponse, tags=["5. Foods & Meal Planning"])
def get_meal_plan(meal_plan_id: str):
    if meal_plan_id not in meal_plans_db:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    return meal_plans_db[meal_plan_id]


# --- 6. AI ENGINE & HUMAN-IN-THE-LOOP WORKFLOW ---

@app.post("/api/v1/ai/generate-plan", tags=["6. AI Engine & HITL Workflow"])
def trigger_ai_plan(data: AIGenerateRequest):
    rec_id = f"rec_{uuid.uuid4().hex[:8]}"
    rec_data = {
        "recommendation_id": rec_id,
        "client_id": data.client_id,
        "dietary_goal": data.dietary_goal,
        "status": "PENDING_REVIEW",
        "generated_plan": ["AI Plan Option A", "AI Plan Option B"]
    }
    ai_recommendations_db[rec_id] = rec_data
    return {"message": "AI recommendation drafted", "recommendation": rec_data}

@app.get("/api/v1/ai/recommendations/pending", tags=["6. AI Engine & HITL Workflow"])
def get_pending_recommendations():
    pending = [r for r in ai_recommendations_db.values() if r["status"] == "PENDING_REVIEW"]
    return pending

@app.patch("/api/v1/ai/recommendations/{recommendation_id}", tags=["6. AI Engine & HITL Workflow"])
def review_ai_recommendation(recommendation_id: str, data: RecommendationReview):
    if recommendation_id not in ai_recommendations_db:
        raise HTTPException(status_code=404, detail="Recommendation ID not found")
    ai_recommendations_db[recommendation_id]["status"] = data.action
    if data.notes:
        ai_recommendations_db[recommendation_id]["review_notes"] = data.notes
    return {"message": f"Recommendation status updated to {data.action}", "recommendation": ai_recommendations_db[recommendation_id]}
