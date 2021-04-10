function update_time(elem) {
  var { value } = elem;

  // Show time selector
  var container = document.querySelector("#time-select-container");
  container.classList.replace("d-none", "d-block");

  // Get the week day selected by user
  var date = new Date(value);
  var selectedDay =  date.toLocaleDateString('en-US', {weekday: 'long'}).toLowerCase();


  var select = document.querySelector("select#time-select");
  select.selectedIndex = 0; // Set selected value to default one
  var optionsArray = select.querySelectorAll("option");

  // Hide or show hours (options) depending on the day selected by user
  optionsArray.forEach((option, index) => {
    console.log(option.dataset.day);
    if (option.dataset.day == selectedDay && option.classList.contains("d-none"))
      option.classList.replace("d-none", "d-block");
    else {
      if (!option.classList.contains("d-none"))
        option.classList.replace("d-block", "d-none");
    }
  });
}
