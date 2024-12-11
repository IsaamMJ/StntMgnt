let students = []; // Array to store student data

// Add student
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('addStudentForm');
    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();

            // Get form values
            const firstName = document.getElementById('firstName').value;
            const lastName = document.getElementById('lastName').value;
            const dateOfBirth = document.getElementById('dateOfBirth').value;
            const studentClass = document.getElementById('class').value;

            // Add student to array
            const newStudent = {
                id: students.length + 1,
                firstName,
                lastName,
                dateOfBirth,
                class: studentClass
            };
            students.push(newStudent);

            // Redirect back to homepage
            window.location.href = 'index.html';
        });
    }
});

// Render table
function renderTable() {
    const tableBody = document.getElementById('studentsTable').querySelector('tbody');
    tableBody.innerHTML = ''; // Clear current rows

    students.forEach(student => {
        const row = `
            <tr>
                <td>${student.id}</td>
                <td>${student.firstName}</td>
                <td>${student.lastName}</td>
                <td>${student.dateOfBirth}</td>
                <td>${student.class}</td>
            </tr>
        `;
        tableBody.innerHTML += row;
    });
}

// Search student
function searchStudent() {
    const query = document.getElementById('search').value.toLowerCase();
    const filteredStudents = students.filter(student =>
        student.firstName.toLowerCase().includes(query) ||
        student.lastName.toLowerCase().includes(query) ||
        student.id.toString() === query
    );

    // Render filtered results
    const tableBody = document.getElementById('studentsTable').querySelector('tbody');
    tableBody.innerHTML = '';
    filteredStudents.forEach(student => {
        const row = `
            <tr>
                <td>${student.id}</td>
                <td>${student.firstName}</td>
                <td>${student.lastName}</td>
                <td>${student.dateOfBirth}</td>
                <td>${student.class}</td>
            </tr>
        `;
        tableBody.innerHTML += row;
    });
}

// Load students on homepage
document.addEventListener('DOMContentLoaded', function () {
    if (document.getElementById('studentsTable')) {
        renderTable();
    }
});
