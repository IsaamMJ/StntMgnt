function transform(line) {
    try {
        // Handle quoted CSV values properly
        var values = line.match(/(".*?"|[^",\s]+)(?=\s*,|\s*$)/g).map(v => v.replace(/^"|"$/g, '').trim());

        var obj = {};

        // Map CSV columns to JSON fields (Ensure that missing or empty values are handled)
        obj.Academic_Year = values[0] || null;
        obj.Admission_No = values[1] || null;
        obj.Admission_Date = values[2] || null;
        obj.First_Name = values[3] || null;
        obj.Last_Name = values[4] || null;
        obj.Gender = values[5] || null;
        obj.Date_of_Birth = values[6] || null;
        obj.Student_Type = values[7] || null;
        obj.Class = values[8] || null;
        obj.Specialization = values[9] || null;
        obj.Section = values[10] || null;
        obj.Registration_EMIS_No = values[11] || null;
        obj.Religion = values[12] || null;
        obj.Caste = values[13] || null;
        obj.Caste_and_Category = values[14] || null;
        obj.Blood_Group = values[15] || null;
        obj.Student_Mobile_No = values[16] || null;
        obj.Student_Email_Id = values[17] || null;
        obj.Mother_Tongue = values[18] || null;
        obj.Aadhar_No = values[19] || null;
        obj.Nationality = values[20] || null;
        obj.Sibling_Name = values[21] || null;
        obj.Sibling_Admission_No_and_Class = values[22] || null;
        obj["Father's_Name"] = values[23] || null;
        obj["Father's_Mobile_No"] = values[24] || null;
        obj["Father's_Email_Id"] = values[25] || null;
        obj["Father's_Occupation"] = values[26] || null;
        obj["Mother's_Name"] = values[27] || null;
        obj["Mother's_Mobile_No"] = values[28] || null;
        obj["Mother's_Email_Id"] = values[29] || null;
        obj["Mother's_Occupation"] = values[30] || null;
        obj["Guardian's_Name"] = values[31] || null;
        obj["Guardian's_Mobile_No"] = values[32] || null;
        obj["Guardian's_Email_Id"] = values[33] || null;
        obj["Guardian's_Occupation"] = values[34] || null;
        obj.Primary_Person = values[35] || null;

        // Convert annual incomes and handle invalid number conversion gracefully
        obj["Father's_Annual_Income"] = parseFloat(values[36]) || null;
        obj["Mother's_Annual_Income"] = parseFloat(values[37]) || null;
        obj["Guardian's_Annual_Income"] = parseFloat(values[38]) || null;

        // Addresses and file links
        obj.Permanent_Address = values[39] || null;
        obj.Present_Address = values[40] || null;
        obj.Same_as_Permanent_Address = values[41] === 'TRUE'; // Boolean conversion
        obj.Student_Photo = values[42] || null;
        obj.Birth_Certificate = values[43] || null;
        obj.Transfer_Certificate = values[44] || null;
        obj.Aadhaar_UIDAI = values[45] || null;
        obj.PAN_Card = values[46] || null;

        // Attachments
        obj.Attachment_1 = values[47] || null;
        obj.Attachment_2 = values[48] || null;
        obj.Attachment_3 = values[49] || null;

        // Return the object as a JSON string or object
        return obj; // Returning the object, JSON.stringify can be done later in the pipeline
    } catch (error) {
        console.error("Error processing line:", line, error);
        return null; // Return null if an error occurs
    }
}
