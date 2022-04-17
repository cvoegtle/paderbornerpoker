function copyToClipboardAndStart() {
  let url_field = document.getElementById("url");
  navigator.clipboard.writeText(url_field.value);
  location.replace(uniqueUrl("/table"));
}

function updateCreateButtonStatus() {
  let createButton = document.getElementById(name="create_button");
  let disabled =  !containsText("table_name") || !containsText("user_name");
  createButton.disabled = disabled;
}

function updateJoinButtonStatus() {
  let joinButton = document.getElementById(name = "join_button");
  let disabled = !containsText("user_name");
  joinButton.disabled = disabled;
}

function onToggleAutoUpdate() {
  document.cookie = `AUTO_UPDATE=${isAutoUpdateEnabled() ? "ON" : "OFF"}`
}

function onTogglePreviewMyCard() {
  document.cookie = `PREVIEW_MY_CARD=${isPreviewMyCardEnabled() ? "ON" : "OFF"}`
  location.replace(uniqueUrl("/table"));
}

function isAutoUpdateEnabled() {
  return isCheckBoxEnabled("auto_update");
}

function isPreviewMyCardEnabled() {
  return isCheckBoxEnabled("preview_my_card")
}

function isCheckBoxEnabled(elementId) {
  let checkbox = document.getElementById(elementId);
  return checkbox.checked;
}

function containsText(elementName) {
  let element = document.getElementById(elementName);
  return element.value != null && element.value.trim().length > 0;
}

class TableObserver {
  pollInterval = 5000;
  intervalId = null;
  pollCount = 0;

  start() {
    this.intervalId = window.setInterval(this.checkForUpdates, this.pollInterval, this);
  }

  processResponse(responseText) {
    let lastUpdate = getCookie("TABLE_UPDATE");
    if (responseText != lastUpdate) {
      this.pollCount = 0;
      location.replace(uniqueUrl("/table"));
    }
    if (this.pollCount >= 30) {
      this.pollInterval = 30000;
      this.stopInterval();
      this.start();
    }
    if (this.pollCount >= 60) {
      this.stopInterval();
    }
  }

  processError() {
    console.log("failed to check whose turn. Stop polling");
    this.stopInterval();
  }

  stopInterval() {
    window.clearInterval(this.intervalId);
  }

  checkForUpdates(that) {
    this.pollCount++;
    if (isAutoUpdateEnabled()) {
      that.pollServerForChange(processResponse, processError)
    }
  }

  pollServerForChange(responseCallback, errorCallback) {
    let ajaxRequest = new XMLHttpRequest();
    ajaxRequest.onload = function () {
      responseCallback(ajaxRequest.responseText)
    };
    ajaxRequest.onerror = function() {
      errorCallback();
    }

    ajaxRequest.open("get", uniqueUrl("/check_for_updates"), true);
    ajaxRequest.send();
  }
}

function uniqueUrl(url) {
  return `${url}?unique=${new Date().getTime()}`;
}

gameObserver = new TableObserver();
function backgroundCheck() {
  gameObserver.start();
}

function processResponse(responseText) {
  gameObserver.processResponse(responseText)
}

function processError() {
  gameObserver.processError();
}

function getCookie(cookieName) {
  let name = cookieName + "=";
  let decodedCookie = decodeURIComponent(document.cookie);
  let ca = decodedCookie.split(';');
  for(let i = 0; i <ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

