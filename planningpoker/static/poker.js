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

function onTogglePreviewMyCard() {
  document.cookie = `PREVIEW_MY_CARD=${isPreviewMyCardEnabled() ? "ON" : "OFF"}`;
  location.replace(uniqueUrl("/table"));
}

function isPreviewMyCardEnabled() {
  return isCheckBoxEnabled("preview_my_card");
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
  isUpdating = false;

  start() {
    this.stop();
    let tableId = getCookie("POKER_TABLE");
    let sseUrl = uniqueUrl(`/table/events${tableId ? "?table_id=" + encodeURIComponent(tableId) : ""}`);
    this.eventSource = new EventSource(sseUrl);

    this.eventSource.onmessage = (event) => {
      let responseText = event.data;
      if (responseText && responseText !== "keep-alive") {
        this.processResponse(responseText);
      }
    };

    this.eventSource.onerror = (err) => {
      console.warn("SSE-Verbindung unterbrochen, automatischer Reconnect...", err);
    };
  }

  stop() {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }

  processResponse(responseText) {
    let lastUpdate = getCookie("TABLE_UPDATE");
    if (responseText != lastUpdate && !this.isUpdating) {
      this.refreshTable(responseText);
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
}

function uniqueUrl(url) {
  let separator = url.indexOf('?') >= 0 ? '&' : '?';
  return `${url}${separator}unique=${new Date().getTime()}`;
}

gameObserver = new TableObserver();
function backgroundCheck() {
  gameObserver.start();
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
