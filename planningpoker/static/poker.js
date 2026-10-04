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
  eventSource = null;
  pollInterval = 5000;
  intervalId = null;
  pollCount = 0;
  isUpdating = false;

  start() {
    if (window.EventSource) {
      this.startSSE();
    } else {
      this.startPolling();
    }
  }

  startSSE() {
    this.stop();
    try {
      let tableId = getCookie("POKER_TABLE");
      let sseUrl = uniqueUrl(`/table/events${tableId ? "?table_id=" + encodeURIComponent(tableId) : ""}`);
      this.eventSource = new EventSource(sseUrl);

      this.eventSource.onmessage = (event) => {
        if (!isAutoUpdateEnabled()) {
          return;
        }
        let responseText = event.data;
        if (responseText && responseText !== "keep-alive") {
          this.processResponse(responseText);
        }
      };

      this.eventSource.onerror = (err) => {
        console.warn("SSE-Verbindung unterbrochen, automatischer Reconnect...", err);
      };
    } catch (e) {
      console.error("Fehler beim Starten von SSE, Fallback auf Polling:", e);
      this.startPolling();
    }
  }

  startPolling() {
    this.stopInterval();
    this.intervalId = window.setInterval(this.checkForUpdates, this.pollInterval, this);
  }

  stop() {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    this.stopInterval();
  }

  stopInterval() {
    if (this.intervalId) {
      window.clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  processResponse(responseText) {
    let lastUpdate = getCookie("TABLE_UPDATE");
    if (responseText != lastUpdate && !this.isUpdating) {
      this.pollCount = 0;
      this.refreshTable(responseText);
    }
    if (this.intervalId) {
      if (this.pollCount >= 30) {
        this.pollInterval = 30000;
        this.startPolling();
      }
      if (this.pollCount >= 60) {
        this.stopInterval();
      }
    }
  }

  refreshTable(newUpdateId) {
    this.isUpdating = true;
    fetch(uniqueUrl("/table"))
      .then((response) => {
        if (!response.ok) {
          throw new Error("HTTP-Fehler " + response.status);
        }
        return response.text();
      })
      .then((htmlText) => {
        let parser = new DOMParser();
        let doc = parser.parseFromString(htmlText, "text/html");
        let newForm = doc.getElementById("formular");
        let currentForm = document.getElementById("formular");
        if (newForm && currentForm) {
          currentForm.innerHTML = newForm.innerHTML;
          document.body.className = doc.body.className;
          let newHeading = doc.querySelector("h1");
          if (newHeading) {
            document.querySelector("h1").innerText = newHeading.innerText;
          }
          if (newUpdateId) {
            document.cookie = `TABLE_UPDATE=${newUpdateId}; path=/`;
          }
        } else {
          location.replace(uniqueUrl("/table"));
        }
      })
      .catch((err) => {
        console.warn("DOM-Aktualisierung fehlgeschlagen, lade Seite neu...", err);
        location.replace(uniqueUrl("/table"));
      })
      .finally(() => {
        this.isUpdating = false;
      });
  }

  processError() {
    console.log("failed to check whose turn. Stop polling");
    this.stopInterval();
  }

  checkForUpdates(that) {
    if (!that) that = this;
    that.pollCount++;
    if (isAutoUpdateEnabled()) {
      that.pollServerForChange(processResponse, processError);
    }
  }

  pollServerForChange(responseCallback, errorCallback) {
    let ajaxRequest = new XMLHttpRequest();
    ajaxRequest.onload = function () {
      responseCallback(ajaxRequest.responseText);
    };
    ajaxRequest.onerror = function () {
      errorCallback();
    };

    ajaxRequest.open("get", uniqueUrl("/check_for_updates"), true);
    ajaxRequest.send();
  }
}

function uniqueUrl(url) {
  let separator = url.indexOf('?') >= 0 ? '&' : '?';
  return `${url}${separator}unique=${new Date().getTime()}`;
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

