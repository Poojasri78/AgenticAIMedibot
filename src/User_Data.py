import json
import random
from faker import Faker
from datetime import datetime, timedelta

# Initialize Faker to generate synthetic data
fake = Faker()

# --- Configuration ---
NUM_USERS = 100  # Number of synthetic users to generate

# --- Master Data Lists (Expand these for more variety) ---
COMMON_ALLERGIES = [
    "Penicillin", "Sulfa drugs", "Aspirin", "Ibuprofen", "Codeine", "Latex",
    "Peanuts", "Shellfish", "Pollen", "Dust Mites", "None"
]

CHRONIC_CONDITIONS = [
    "Hypertension", "Type 2 Diabetes", "Asthma", "Arthritis", "Hypothyroidism",
    "Chronic Kidney Disease", "Depression", "Migraine", "None"
]

PHARMA_PRODUCTS = {
    # OTC = Over-the-counter, Rx = Prescription
    "Pain Relief": [
        {"name": "Paracetamol 500mg", "type": "OTC"},
        {"name": "Ibuprofen 200mg", "type": "OTC"},
        {"name": "Aspirin 75mg", "type": "OTC"},
        {"name": "Tramadol 50mg", "type": "Rx"},
    ],
    "Allergy": [
        {"name": "Cetirizine 10mg", "type": "OTC"},
        {"name": "Loratadine 10mg", "type": "OTC"},
        {"name": "Fexofenadine 180mg", "type": "Rx"},
    ],
    "Diabetes": [
        {"name": "Metformin 500mg", "type": "Rx"},
        {"name": "Gliclazide 80mg", "type": "Rx"},
        {"name": "Insulin Glargine", "type": "Rx"},
    ],
    "Hypertension": [
        {"name": "Amlodipine 5mg", "type": "Rx"},
        {"name": "Lisinopril 10mg", "type": "Rx"},
        {"name": "Losartan 50mg", "type": "Rx"},
    ],
    "Vitamins": [
        {"name": "Vitamin D3 1000 IU", "type": "OTC"},
        {"name": "Vitamin C 500mg", "type": "OTC"},
        {"name": "Multivitamin Complex", "type": "OTC"},
    ]
}

def generate_user_profile(user_id):
    """Generates a single synthetic user profile."""
    profile = fake.profile()
    return {
        "user_id": f"USER_{user_id:04d}",
        "name": profile['name'],
        "gender": profile.get('sex', random.choice(['M', 'F'])),
        "date_of_birth": profile['birthdate'].strftime('%Y-%m-%d'),
        "address": profile['address'].replace('\n', ', '),
        "email": profile['mail'],
        "phone_number": fake.phone_number(),
    }

def generate_medical_info():
    """Generates medical history for a user."""
    allergies = random.sample(
        COMMON_ALLERGIES, k=random.randint(0, 3)
    )
    # Ensure 'None' is exclusive
    if len(allergies) > 1 and "None" in allergies:
        allergies.remove("None")
    if not allergies:
        allergies = ["None"]

    conditions = random.sample(
        CHRONIC_CONDITIONS, k=random.randint(0, 2)
    )
    if len(conditions) > 1 and "None" in conditions:
        conditions.remove("None")
    if not conditions:
        conditions = ["None"]

    return {
        "allergies": allergies,
        "chronic_conditions": conditions
    }

def generate_purchase_history(user_id, medical_info):
    """Generates a list of past purchases for a user."""
    purchases = []
    num_purchases = random.randint(3, 15)
    
    # Create a pool of relevant drugs for the user
    drug_pool = []
    for category in PHARMA_PRODUCTS.values():
        drug_pool.extend(category)
        
    if "Hypertension" in medical_info["chronic_conditions"]:
        drug_pool.extend(PHARMA_PRODUCTS["Hypertension"] * 3) # Increase likelihood
    if "Type 2 Diabetes" in medical_info["chronic_conditions"]:
        drug_pool.extend(PHARMA_PRODUCTS["Diabetes"] * 3)

    for i in range(num_purchases):
        drug = random.choice(drug_pool)
        purchase_date = fake.date_time_between(start_date="-2y", end_date="now")
        
        purchase = {
            "order_id": f"ORD_{user_id.split('_')[1]}_{i+1:03d}",
            "drug_name": drug['name'],
            "is_prescription": drug['type'] == 'Rx',
            "quantity": random.randint(1, 3),
            "purchase_date": purchase_date.strftime('%Y-%m-%d %H:%M:%S'),
            "pharmacy": f"{fake.company()} Pharmacy"
        }
        purchases.append(purchase)
        
    # Sort purchases by date
    purchases.sort(key=lambda x: x['purchase_date'], reverse=True)
    return purchases

def generate_prescriptions(user_id, purchase_history):
    """Generates prescription details based on Rx purchases."""
    prescriptions = []
    rx_purchases = [p for p in purchase_history if p['is_prescription']]
    
    # Create unique prescriptions from the purchase history
    unique_rx_drugs = {p['drug_name'] for p in rx_purchases}

    for drug_name in unique_rx_drugs:
        # Find the latest purchase for this drug to base the prescription on
        latest_purchase = max(
            [p for p in rx_purchases if p['drug_name'] == drug_name],
            key=lambda x: x['purchase_date']
        )
        
        issue_date = datetime.strptime(latest_purchase['purchase_date'], '%Y-%m-%d %H:%M:%S') - timedelta(days=random.randint(2, 5))
        
        prescription = {
            "prescription_id": f"RX_{user_id.split('_')[1]}_{len(prescriptions)+1:02d}",
            "drug_name": drug_name,
            "doctor_name": f"Dr. {fake.last_name()}",
            "issue_date": issue_date.strftime('%Y-%m-%d'),
            "dosage": drug_name.split(' ')[-1], # Simple dosage extraction
            "refills_remaining": random.randint(0, 5),
            "is_auto_refill_enabled": random.choice([True, False])
        }
        prescriptions.append(prescription)
        
    return prescriptions


def main():
    """Main function to generate the dataset."""
    full_dataset = []
    print(f"Generating synthetic data for {NUM_USERS} users...")

    for i in range(1, NUM_USERS + 1):
        user_profile = generate_user_profile(i)
        medical_info = generate_medical_info()
        
        # Combine user and medical info
        user_data = {**user_profile, **medical_info}
        
        purchase_history = generate_purchase_history(user_data['user_id'], medical_info)
        prescriptions = generate_prescriptions(user_data['user_id'], purchase_history)
        
        user_data['purchase_history'] = purchase_history
        user_data['prescriptions'] = prescriptions
        
        full_dataset.append(user_data)

    # Save to a JSON file
    file_path = "Synthetic_User_Data.json"
    with open(file_path, 'w') as f:
        json.dump(full_dataset, f, indent=4)
        
    print(f"\nSuccessfully generated dataset!")
    print(f"Data saved to '{file_path}'")


if __name__ == "__main__":
    main()
