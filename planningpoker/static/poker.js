function copyToClipboardAndStart() {
  let url_field = document.getElementById("url");
  navigator.clipboard.writeText(url_field.value);
  location.replace("/");
}
