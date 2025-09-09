function showLoader(message) {
  const loader = document.getElementById("loader");
  document.getElementById("loader-text").textContent = message;
  loader.style.display = "flex";
}

function hideLoader() {
  const loader = document.getElementById("loader");
  loader.style.display = "none";
}
icon.addEventListener("click", async () => {
  try {
    const text = await navigator.clipboard.readText();
    document.querySelector("#input").value = text;
  } catch (err) {
    alert("Clipboard access failed. Please try again.");
  }
});
document.addEventListener("DOMContentLoaded", () => {
  const btn = document.querySelector("#btnn");

  function isValidYouTubeUrl(url) {
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$/;
    return youtubeRegex.test(url);
}

btn.addEventListener("click", async function (e) {
    e.preventDefault();

    const url = document.querySelector("#input").value.trim();
    const container = document.querySelector("#video-container");
    container.innerHTML = "";

    if (!url) {
        container.innerHTML = `<div class="error-msg">Enter a valid URL</div>`;
        return;
    }

    // Client-side validation
    if (!isValidYouTubeUrl(url)) {
        container.innerHTML = `<div class="error-msg">Please enter a valid YouTube URL</div>`;
        return;
    }

    try {
      showLoader("Fetching video info...");

      const res = await fetch("/info", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url })
      });

      hideLoader(); // hide after fetch response

      const data = await res.json();
      if (data.error) {
        container.innerHTML = `<div class="error-msg">${data.error}</div>`;
        return;
      }

      // Video info container
      const newDiv = document.createElement("div");
      newDiv.classList.add("title-div");
      newDiv.style.background = "white";
      newDiv.style.padding = "10px";
      newDiv.style.marginTop = "10px";
      newDiv.style.textAlign = "center";
      newDiv.style.borderRadius = "10px";
      newDiv.style.boxShadow = "0 2px 6px rgba(0,0,0,0.1)";

      const title = document.createElement("h3");
      title.innerText = data.title;
      newDiv.appendChild(title);

      const thumbnail = document.createElement("img");
      thumbnail.src = data.thumbnail;
      thumbnail.style.width = "100%";
      thumbnail.style.maxWidth = "320px";
      thumbnail.style.borderRadius = "10px";
      thumbnail.style.marginTop = "10px";
      newDiv.appendChild(thumbnail);

      // Quality buttons
      const qualityBox = document.createElement("div");
      qualityBox.style.marginTop = "15px";

      const seenResolutions = new Set();
      data.video_formats.forEach(f => {
        const resLabel = `${f.height || "?"}p`;

        if (seenResolutions.has(resLabel)) return;
        seenResolutions.add(resLabel);

        const qBtn = document.createElement("button");
        qBtn.innerText = resLabel;
        qBtn.style.margin = "5px";
        qBtn.style.padding = "8px 12px";
        qBtn.style.borderRadius = "6px";
        qBtn.style.border = "1px solid #1750a0";
        qBtn.style.background = "white";
        qBtn.style.color = "#1750a0";
        qBtn.style.cursor = "pointer";

        qBtn.addEventListener("mouseover", () => {
          qBtn.style.background = "#1750a0";
          qBtn.style.color = "white";
        });
        qBtn.addEventListener("mouseout", () => {
          qBtn.style.background = "white";
          qBtn.style.color = "#1750a0";
        });

        qBtn.addEventListener("click", async () => {
          try {
            // ✅ Show loader while downloading
            showLoader(`Downloading ${resLabel}...`);

            const res = await fetch("/download", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ url, format_id: f.format_id })
            });

            hideLoader(); // hide after response

            if (!res.ok) {
              alert("Download failed.");
              return;
            }

            const blob = await res.blob();
            const a = document.createElement("a");
            a.href = URL.createObjectURL(blob);
            a.download = `${data.title}.mp4`;
            a.click();
          } catch (err) {
            hideLoader();
            alert("Error during download.");
          }
        });

        qualityBox.appendChild(qBtn);
      });

      newDiv.appendChild(qualityBox);
      container.appendChild(newDiv);

    } catch (err) {
      hideLoader();
      container.innerHTML = `<div class="error-msg">Error fetching video info.</div>`;
    }
  });
});
