function toggleTab(evt, tabName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
      tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("nav-link");
    for (i = 0; i < tablinks.length; i++) {
      tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}

$( document ).ready(function() {
    if( document.getElementById("people-data") != null){
        people_data = $('#people-data').data();
        console.log(people_data.table);
        if(people_data.table == "consultants"){
            document.getElementById("manageConsultants").click();
            if(people_data.action == "create"){
                toggleForm('ConsultantForm');
            }
        }else if(people_data.table == "contractors"){
            document.getElementById("manageContractors").click();
            if(people_data.action == "create"){
                toggleForm('ContractorForm');
            }
        }else if(people_data.table == "employees"){
            document.getElementById("manageEmployees").click();
            if(people_data.action == "create" || people_data.action == "edit"){
                toggleForm('EmployeeForm');
                fetchData('profiles','#employee_profile_id');
            }
        }else if(people_data.table == "profiles"){
            if(people_data.action == "create" || people_data.action == "edit"){
                toggleForm('ProfileForm');
            }
        }else if(people_data.table == "joblisting"){
            document.getElementById("manageJobListing").click();
            if(people_data.action == "create" || people_data.action == "edit"){
                toggleForm('JobListing');
            }
        }else if(people_data.table == "details"){
            document.getElementById("managePayroll").click();
            if(people_data.action == "create" || people_data.action == "edit"){
                toggleForm('Payroll');
            }
        }
    }
});

function toggleForm(formId) {
    if(document.getElementById(formId).style.display == "block"){
        document.getElementById(formId).style.display = "none";
    }else{
        document.getElementById(formId).style.display = "block";
    }
}


function autoFillEmail(username) {
    document.getElementById("employee-email").value = username + "@hrs.com";
}

function fetchData(tableName, fieldId) {
    let url = '/fetchData/' + tableName
    fetch(url)
    .then((response) => {
        console.log(response.status);
        return response.json();
    })
    .then(function(data) {
        console.log(data.profiles);
        let dropdown = $(fieldId);
        dropdown.empty();
        for (var i = 0; i < data.profiles.length; i++) {
            dropdown.append($('<option></option>').attr('value', data.profiles[i].id).text( data.profiles[i].profile_name));
        }
    });
}