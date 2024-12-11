from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from google.cloud import storage, bigquery
import json
import os

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = "your-secret-key"  # Required for flash messages

# Set up your GCS bucket name and project ID
BUCKET_NAME = "06_stntmgntmodule1"
PROJECT_ID = "sinuous-branch-444014-t6"
BUCKET_NAME1 = "06strglake"

# Path to save the admission series settings
ADMISSION_SERIES_FILE = 'admission_series.json'

def load_admission_series():
    """Load the admission series settings from a JSON file"""
    if os.path.exists(ADMISSION_SERIES_FILE):
        with open(ADMISSION_SERIES_FILE, 'r') as f:
            admission_series = json.load(f)
    else:
        # Default values if no settings file exists
        admission_series = {
            'start_number': 1000,  # Starting admission number
            'increment': 1,        # Increment by 1 for each new student
            'grades': {  
                'PreKG': 3,
                'LKG': 4,
                'UKG': 2,          # Default grade section count
                'Grade 1': 3,
                'Grade 2': 3,
                'Grade 3': 3,
                'Grade 4': 3,
                'Grade 5': 3,
                'Grade 6': 3,
                'Grade 7': 3,
                'Grade 8': 3,
                'Grade 9': 3,
                'Grade 10': 3,
                'Grade 11': 3,
                'Grade 12': 3,
            }
        }

    # Ensure the 'grades' key exists in case it's missing or malformed in the file
    if 'grades' not in admission_series:
        admission_series['grades'] = {
            'PreKG': 3,
            'LKG': 4,
            'UKG': 2,   
            'Grade 1': 3,
            'Grade 2': 3,
            'Grade 3': 3,
            'Grade 4': 3,
            'Grade 5': 3,
            'Grade 6': 3,
            'Grade 7': 3,
            'Grade 8': 3,
            'Grade 9': 3,
            'Grade 10': 3,
            'Grade 11': 3,
            'Grade 12': 3,
        }

    return admission_series


def save_admission_series(start_number, increment, grades):
    """Save the admission series settings to a JSON file"""
    with open(ADMISSION_SERIES_FILE, 'w') as f:
        json.dump({'start_number': start_number, 'increment': increment, 'grades': grades}, f)

@app.route('/admission-series', methods=['GET', 'POST'])
def admission_series():
    """Handle the Admission Number Series settings"""
    admission_series = load_admission_series()  # Load the current settings

    if request.method == 'POST':
        # Get the submitted values from the form
        start_number = int(request.form['start_number'])
        increment = int(request.form['increment'])
        
        # Update the number of sections for each grade
        grades = {}
        for grade in admission_series['grades']:
            grade_key = f"sections_{grade}"
            if grade_key in request.form:
                grades[grade] = int(request.form[grade_key])
            else:
                grades[grade] = admission_series['grades'].get(grade, 3)  # Default to 3 sections if not provided

        # Save the new settings
        save_admission_series(start_number, increment, grades)
        flash("Admission Number Series and Grade Sections updated successfully!", "success")
        
        # Redirect to the same page to load and display the updated values
        return redirect(url_for('admission_series'))
    
    # After updating, display the current settings
    return render_template('admission_series.html', admission_series=admission_series)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle student registration"""
    admission_series = load_admission_series()  # Get the current admission number settings

    if request.method == 'POST':
        # Extract submitted form data
        student_name = request.form.get('student_name')
        grade = request.form.get('grade')
        section = request.form.get('section')

        if not student_name or not grade or not section:
            flash("Please provide all required details (Name, Grade, Section).", "error")
            return redirect(url_for('register'))

        # Generate the admission number for the new student
        admission_number = admission_series['start_number']

        # Increment the admission number for the next student
        admission_series['start_number'] += admission_series['increment']
        save_admission_series(admission_series['start_number'], admission_series['increment'], admission_series['grades'])  # Save the updated series

        # Placeholder for saving student data to DB (or any other processing logic)
        # You can replace this part with actual database insertion code
        flash(f"Student '{student_name}' registered successfully with Admission Number: {admission_number}", "success")
        return redirect(url_for('register'))

    # Pass the current admission number and grades with sections to the template
    grades = admission_series['grades']
    return render_template(
        'register.html', 
        admission_number=admission_series['start_number'], 
        grades=grades
    )



def upload_to_gcs(file, bucket_name, filename):
    """Uploads a file to the specified GCS bucket."""
    try:
        client = storage.Client(project=PROJECT_ID)
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(filename)
        blob.upload_from_file(file, content_type=file.content_type)
        return f"gs://{bucket_name}/{filename}"
    except Exception as e:
        raise RuntimeError(f"Failed to upload to GCS: {e}")

def fetch_students_from_bigquery():
    """Fetch student data from BigQuery."""
    try:
        client = bigquery.Client(project=PROJECT_ID)
        query = """
            SELECT 
              `Admission_No`, 
              `First_Name`, 
              `Last_Name`, 
              `Date_of_Birth`, 
              `Class`
            FROM `stndmgnt06.stndmgnt6`
            LIMIT 50
        """
        query_job = client.query(query)
        students = []
        for row in query_job:
            students.append({
                "Admission_No": row["Admission_No"],  # Match the column name with leading space
                "First_Name": row["First_Name"],      # Match the column name with leading space
                "Last_Name": row["Last_Name"],        # Match the column name with leading space
                "Date_of_Birth": row["Date_of_Birth"],# Match the column name with leading space
                "Class": row["Class"],                # Match the column name with leading space
            })
        return students
    except Exception as e:
        print(f"Error fetching data from BigQuery: {e}")
        flash(f"Error fetching data from BigQuery: {e}", "error")
        return []


@app.route("/")
def index():
    """Render the home page and display student data from BigQuery."""
    students = fetch_students_from_bigquery()
    print("Students fetched for index page:", students)  # Debugging log
    return render_template("index.html", students=students)
   

@app.route("/upload", methods=["GET", "POST"])
def upload():
    """Render the upload form and handle file upload."""
    if request.method == "POST":
        # Handle file upload
        if "file" not in request.files:
            flash("No file part in the request.", "error")
            return redirect(url_for("upload"))

        file = request.files["file"]

        if file.filename == "":
            flash("No file selected.", "error")
            return redirect(url_for("upload"))

        try:
            # Sanitize filename (optional: implement further sanitization if needed)
            filename = file.filename
            gcs_path = upload_to_gcs(file, BUCKET_NAME, filename)
            flash(f"File uploaded successfully: <a href='{gcs_path}'>{gcs_path}</a>", "success")
            return redirect(url_for("upload"))
        except Exception as e:
            flash(f"An error occurred: {e}", "error")
            return redirect(url_for("upload"))

    # If GET request, render the upload page
    return render_template("upload.html")

@app.route('/get-sections')
def get_sections():
    """API to fetch the number of sections for a selected class."""
    grade = request.args.get('class')  # Get the class from the query parameters
    if not grade:
        return {"success": False, "error": "Class not provided."}

    # Load the admission series settings
    admission_series = load_admission_series()
    grades = admission_series.get("grades", {})

    # Get the section count for the selected class
    section_count = grades.get(grade)
    if section_count is None:
        return {"success": False, "error": f"Class '{grade}' not found in settings."}


    return {"success": True, "sectionCount": section_count}

@app.route('/fetch-family-data', methods=['GET'])
def fetch_family_data():
    """Fetch family data from BigQuery based on sibling admission number."""
    sibling_admission_no = request.args.get('sibling_admission_no')
    
    if not sibling_admission_no:
        return {"success": False, "error": "Sibling Admission Number is required."}

    try:
        client = bigquery.Client(project=PROJECT_ID)
        
        # BigQuery query to fetch family data
        query = f"""
    SELECT
        First_Name, 
        `Father's_Name`,
        `Father's_Mobile_No`,
        `Father's_Email_Id`,
        `Father's_Occupation`,
        `Mother's_Name`,
        `Mother's_Mobile_No`,
        `Mother's_Email_Id`,
        `Mother's_Occupation`,
        `Guardian's_Name`,
        `Guardian's_Mobile_No`,
        `Guardian's_Email_Id`,
        `Guardian's_Occupation`,
        Primary_Person,
        `Father's_Annual_Income`,
        `Mother's_Annual_Income`,
        `Guardian's_Annual_Income`,
        Permanent_Address,
        Present_Address,
        Same_as_Permanent_Address,
    FROM `stndmgnt06.stndmgnt6`
    WHERE CAST(Admission_No AS STRING) = @sibling_admission_no
"""
        
        # Use parameterized queries to prevent SQL injection
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("sibling_admission_no", "STRING", sibling_admission_no),
            ]
        )
        
        query_job = client.query(query, job_config=job_config)
        result = query_job.result()
        
        # Process query result
        family_data = [dict(row) for row in result]
        if not family_data:
            return {"success": False, "error": "No family data found for the given sibling admission number."}

        return {"success": True, "data": family_data}

    except Exception as e:
        print(f"Error fetching data from BigQuery: {e}")
        return {"success": False, "error": f"Error fetching data: {e}"}

def upload_photo_to_gcs(file, bucket_name, destination_blob_name):
    """Uploads a file to Google Cloud Storage."""
    try:
        if not file:
            return None

        # Create a new Storage Client instance
        client = storage.Client(project=PROJECT_ID)
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        # Upload the file
        blob.upload_from_file(file, content_type=file.content_type)

        # Generate the public URL of the file
        return blob.public_url
    except Exception as e:
        raise Exception(f"Failed to upload photo to GCS: {e}")
    
def insert_family_data_into_bigquery(form_data, photo_url):
    """Insert family data and photo URL into BigQuery."""
    try:
        client = bigquery.Client(project=PROJECT_ID)
        table_id = f"{PROJECT_ID}.stndmgnt06.stndmgnt6"

        # Prepare the row to insert
        rows_to_insert = [
            {
                "siblingName": form_data.get("siblingName"),
                "fatherName": form_data.get("fatherName"),
                "fatherMobile": form_data.get("fatherMobile"),
                "fatherEmail": form_data.get("fatherEmail"),
                "fatherOccupation": form_data.get("fatherOccupation"),
                "motherName": form_data.get("motherName"),
                "motherMobile": form_data.get("motherMobile"),
                "motherEmail": form_data.get("motherEmail"),
                "motherOccupation": form_data.get("motherOccupation"),
                "guardianName": form_data.get("guardianName"),
                "guardianMobile": form_data.get("guardianMobile"),
                "guardianEmail": form_data.get("guardianEmail"),
                "guardianOccupation": form_data.get("guardianOccupation"),
                "photoUrl": photo_url,  # Include the photo URL
            }
        ]
        
        errors = client.insert_rows_json(table_id, rows_to_insert)
        if errors:
            print(f"Errors occurred while inserting into BigQuery: {errors}")
            return False
        else:
            print("Data successfully inserted into BigQuery.")
            return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    
def validate_integer(value, default=0):
    try:
        return int(value) if value else default
    except ValueError:
        return default

    
@app.route('/register-student', methods=['POST'])
def register_student():
    try:
        # Extract form data
        form_data = request.form.to_dict()

        # Handle photo and file uploads
        photo_file = request.files.get("studentPhoto")
        birth_certificate = request.files.get("birthCertificate")
        transfer_certificate = request.files.get("transferCertificate")
        aadhaar_uidai = request.files.get("aadhaarUidai")
        pan_card = request.files.get("panCard")
        attachment_1 = request.files.get("attachment1")
        attachment_2 = request.files.get("attachment2")
        attachment_3 = request.files.get("attachment3")

        # Upload files to GCS
        photo_url = upload_photo_to_gcs(photo_file, BUCKET_NAME1, f"pp/{validate_integer(form_data.get('admissionNo'))}_pp.{photo_file.filename.split('.')[-1]}") if photo_file else None
        birth_certificate_url = upload_photo_to_gcs(birth_certificate, BUCKET_NAME1, f"bc/{validate_integer(form_data.get('admissionNo'))}_bc.{birth_certificate.filename.split('.')[-1]}") if birth_certificate else None
        transfer_certificate_url = upload_photo_to_gcs(transfer_certificate, BUCKET_NAME1, f"tc/{validate_integer(form_data.get('admissionNo'))}_tc.{transfer_certificate.filename.split('.')[-1]}") if transfer_certificate else None
        aadhaar_uidai_url = upload_photo_to_gcs(aadhaar_uidai, BUCKET_NAME1, f"aadhaar/{validate_integer(form_data.get('admissionNo'))}_aadhaar.{aadhaar_uidai.filename.split('.')[-1]}") if aadhaar_uidai else None
        pan_card_url = upload_photo_to_gcs(pan_card, BUCKET_NAME1, f"pan/{validate_integer(form_data.get('admissionNo'))}_pan.{pan_card.filename.split('.')[-1]}") if pan_card else None
        attachment_1_url = upload_photo_to_gcs(attachment_1, BUCKET_NAME1, f"a1/{validate_integer(form_data.get('admissionNo'))}_a1.{attachment_1.filename.split('.')[-1]}") if attachment_1 else None
        attachment_2_url = upload_photo_to_gcs(attachment_2, BUCKET_NAME1, f"a2/{validate_integer(form_data.get('admissionNo'))}_a2.{attachment_2.filename.split('.')[-1]}") if attachment_2 else None
        attachment_3_url = upload_photo_to_gcs(attachment_3, BUCKET_NAME1, f"a3/{validate_integer(form_data.get('admissionNo'))}_a3.{attachment_3.filename.split('.')[-1]}") if attachment_3 else None

        # Prepare data for BigQuery
        row_to_insert = {
            "Academic_Year": form_data.get("academicYear", ""),
            "Admission_No": validate_integer(form_data.get("admissionNo")),
            "Admission_Date": form_data.get("admissionDate", ""),
            "First_Name": form_data.get("firstName", ""),
            "Last_Name": form_data.get("lastName", ""),
            "Gender": form_data.get("gender", ""),
            "Date_of_Birth": form_data.get("dateOfBirth", ""),
            "Student_Type": form_data.get("studentType", ""),
            "Class": form_data.get("class", ""),
            "Specialization": form_data.get("specialization", ""),
            "Section": form_data.get("section", ""),
            "Registration_EMIS_No": form_data.get("registrationEmisNo", ""),
            "Religion": form_data.get("religion", ""),
            "Caste": form_data.get("caste", ""),
            "Caste_and_Category": form_data.get("casteAndCategory", ""),
            "Blood_Group": form_data.get("bloodGroup", ""),
            "Student_Mobile_No": form_data.get("studentMobileNo", ""),
            "Student_Email_Id": form_data.get("studentEmailId", ""),
            "Mother_Tongue": form_data.get("motherTongue", ""),
            "Aadhar_No": validate_integer(form_data.get("aadharNo")),
            "Nationality": form_data.get("nationality", ""),
            "Sibling_Name": form_data.get("siblingName", ""),
            "Sibling_Admission_No_and_Class": form_data.get("siblingAdmissionNoAndClass", ""),
            "Father's_Name": form_data.get("fatherName", ""),
            "Father's_Mobile_No": form_data.get("fatherMobileNo", ""),
            "Father's_Email_Id": form_data.get("fatherEmailId", ""),
            "Father's_Occupation": form_data.get("fatherOccupation", ""),
            "Mother's_Name": form_data.get("motherName", ""),
            "Mother's_Mobile_No": form_data.get("motherMobileNo", ""),
            "Mother's_Email_Id": form_data.get("motherEmailId", ""),
            "Mother's_Occupation": form_data.get("motherOccupation", ""),
            "Guardian's_Name": form_data.get("guardianName", ""),
            "Guardian's_Mobile_No": form_data.get("guardianMobileNo", ""),
            "Guardian's_Email_Id": form_data.get("guardianEmailId", ""),
            "Guardian's_Occupation": form_data.get("guardianOccupation", ""),
            "Primary_Person": form_data.get("primaryPerson", ""),
            "Father's_Annual_Income": validate_integer(form_data.get("fatherAnnualIncome")),
            "Mother's_Annual_Income": validate_integer(form_data.get("motherAnnualIncome")),
            "Guardian's_Annual_Income": validate_integer(form_data.get("guardianAnnualIncome")),
            "Permanent_Address": form_data.get("permanentAddress", ""),
            "Present_Address": form_data.get("presentAddress", ""),
            "Same_as_Permanent_Address": form_data.get("sameAsPermanentAddress", ""),
            "Student_Photo": photo_url,
            "Birth_Certificate": birth_certificate_url,
            "Transfer_Certificate": transfer_certificate_url,
            "Aadhaar_UIDAI": aadhaar_uidai_url,
            "PAN_Card": pan_card_url,
            "Attachment_1": attachment_1_url,
            "Attachment_2": attachment_2_url,
            "Attachment_3": attachment_3_url,
        }

        # Insert data into BigQuery
        client = bigquery.Client(project=PROJECT_ID)
        table_id = f"{PROJECT_ID}.stndmgnt06.stndmgnt6"
        errors = client.insert_rows_json(table_id, [row_to_insert])

        if errors:
            flash(f"Error uploading data to BigQuery: {errors}", "error")
            return jsonify(success=False, error=errors)
        
        flash("Student successfully registered and data uploaded to BigQuery!", "success")
        return jsonify(success=True)

    except Exception as e:
        flash(f"An error occurred: {e}", "error")
        return jsonify(success=False, error=str(e))
    


if __name__ == "__main__":
    app.run(debug=True)
