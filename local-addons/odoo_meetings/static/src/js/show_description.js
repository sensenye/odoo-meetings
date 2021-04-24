// odoo.define("show_description", function (require) {
//   var core = require("web.core");
//   var rpc = require("web.rpc");
//   // alert(core._t('Hello world'));
//   // alert('Holii');

//   // var description = rpc._rpc({
//   //   model: 'odoo_meeting.meeting_type',
//   //   method: 'get_description',
//   //   // args: [some, args],
//   // })

//   // console.log('Hola');
//   // console.log(description);

//   // function listQ() {
//   //   console.log('Hola');
//   //   var e = document.getElementById("meetingTypeSelect");
//   //   console.log(e.selectedIndex);
//   //   if (e.selectedIndex == 1) {
//       // if ("Blank Test" === e.options[e.selectedIndex].value) {
//         alert("yo");
//       // }
//   //   }
//   // }
//   // document.getElementById("meetingTypeSelect").addEventListener("click", listQ);

//   return {
//     // if you created functionality to export, add it here
//   };
// });

function show_description(elem) {
  var { value, selectedIndex } = elem;

  // console.log(value);
  // console.log(selectedIndex);

  var container = document.querySelector("#meetingTypeDescription");
  var descripArray = container.querySelectorAll("div");

  descripArray.forEach((desc, index) => {
    if (desc.classList.contains("d-block"))
      desc.classList.replace("d-block", "d-none");
    if (selectedIndex === index) {
      if (!desc.classList.contains("d-block"))
        desc.classList.replace("d-none", "d-block");
    }
  });
}
