function openPeopleTab(evt, tabName) {
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

document.getElementById("manageEmployees").click();

function toggleForm(evt, formId) {
    console.log(document.getElementById(formId).style.display);
    if(document.getElementById(formId).style.display == "block"){
        document.getElementById(formId).style.display = "none";
    }else{
        document.getElementById(formId).style.display = "block";
    }
}

function fetchProfiles(evt, formId) {
    fetch('/fetchData/profiles')
    .then((response) => {
        console.log(response.status);
        return response.json();
    })
    .then(function(data) {
        console.log(data.profiles);
        let dropdown = $('#profile_id');
        dropdown.empty();
        for (var i = 0; i < data.profiles.length; i++) {
            dropdown.append($('<option></option>').attr('value', data.profiles[i].id).text( data.profiles[i].profile_name));
        }
    });
}