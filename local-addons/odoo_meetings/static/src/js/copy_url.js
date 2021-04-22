function copy_url(aTag) {
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

  // Copy url to clipboard
  const el = document.createElement('textarea');
  el.value = meetingTypeURL;
  document.body.appendChild(el);
  el.select();
  document.execCommand('copy');
  document.body.removeChild(el);

  alert(`La URL del tipo de reunión "${meetingTypeName}" se ha copiado con éxito al portapapeles.`)
}

const convertToKebabCase = (string) => {
  return string.replace(/\s+/g, '-').toLowerCase();
}