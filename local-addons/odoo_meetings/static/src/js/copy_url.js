function copy_url(aTag) {
  var meetingTypeURL = get_meeting_type_url(aTag);
  // Copy url to clipboard
  const el = document.createElement('textarea');
  el.value = meetingTypeURL;
  document.body.appendChild(el);
  el.select();
  document.execCommand('copy');
  document.body.removeChild(el);

  alert(`La URL del tipo de reunión se ha copiado con éxito al portapapeles.`);
  return meetingTypeURL;
}

function download_qr(aTag) {
  var meetingTypeURL = get_meeting_type_url(aTag);
  var meetingTypeName = get_meeting_type_name(aTag);

  var qr_url = `http://api.qrserver.com/v1/create-qr-code/?data=${meetingTypeURL}&size=250x250`;

  var modal = document.getElementById("qr_modal");

  if (modal == null) { // Modal not created in DOM
    // Create a modal using JS
    var mainContainer = document.createElement("div");
    mainContainer.setAttribute("id", "qr_modal");
    mainContainer.classList.add("odoo-meetings-modal");
  
    var modalContent = document.createElement("div");
    modalContent.classList.add("odoo-meetings-modal-content");
  
    var closeBtn = document.createElement("span");
    closeBtn.innerHTML = "X";
    closeBtn.classList.add("odoo-meetings-close");
    closeBtn.setAttribute("onclick", "close_modal()");
  
    var img = document.createElement("img");
    img.setAttribute("src", qr_url);
    
    var title = document.createElement("h2");
    title.innerHTML = meetingTypeName;
    var p = document.createElement("p");
    p.innerHTML = "Escanea o descarga el código QR.";
    var url = document.createElement("p");
    url.innerHTML = meetingTypeURL;
    url.classList.add("pt-3")
    
    // Show modal in the DOM
    mainContainer.append(modalContent);
    modalContent.append(closeBtn);
    modalContent.append(title);
    modalContent.append(p);
    modalContent.append(img);
    modalContent.append(url);
    body = document.querySelector("body");
    body.append(mainContainer);
  } else { // Modal already exists
    // Update qr image, title and url. Also need to update modal visibility
    var img = modal.querySelector("img");
    var title = modal.querySelector("h2");
    var url = modal.querySelectorAll("p");
    img.src = qr_url;
    title.innerHTML = meetingTypeName;
    url[1].innerHTML = meetingTypeURL;
    modal.style.display = "block";
  }
}

const convertToKebabCase = (string) => {
  return string.replace(/\s+/g, '-').toLowerCase();
}

function get_meeting_type_name(aTag) {
  // Get all span with a span tag as father within the a tag
  var spanNodeList = aTag.querySelectorAll('span > span')
  return spanNodeList[1].innerHTML;
}

function get_meeting_type_url(aTag) {
  // Get all span with a span tag as father within the a tag
  var spanNodeList = aTag.querySelectorAll('span > span')

  var id = spanNodeList[0].innerHTML;
  var meetingTypeName = spanNodeList[1].innerHTML;

  // Get base URL
  var getUrl = window.location;
  var baseUrl = getUrl .protocol + "//" + getUrl.host + "/";

  // Convert meeting type name to kebab case
  meetingTypeNameKebab = convertToKebabCase(meetingTypeName);

  // Meeting type url
  var meetingTypeURL = baseUrl + 'odoo-meetings/' + meetingTypeNameKebab + '-' + id + '/';

  return meetingTypeURL;
}

function close_modal() {
  var modal = document.getElementById("qr_modal");
  modal.style.display = "none";
}