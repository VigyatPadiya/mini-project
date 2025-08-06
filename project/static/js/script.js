let icon = document.querySelector("#icon");

icon.addEventListener("click", async () => {
  try {
    const text = await navigator.clipboard.readText();
    document.querySelector("#input").value = text;
    console.log("Clipboard content:", text);
  } catch (err) {
    console.error("Failed to access clipboard", err);
    alert("Clipboard access failed. Please try again.");
  }
});

document.addEventListener("DOMContentLoaded", () => {
  const btn = document.querySelector("#btnn");

  btn.addEventListener("click", function (e) {
    e.preventDefault();

    const urlInput = document.querySelector("input[name='url']");
    const url = urlInput.value.trim();

    // Remove previous error and title div
    const existingError = document.querySelector(".error-msg");
    if (existingError) existingError.remove();

    const existDiv = document.querySelector(".title-div");
    if (existDiv) existDiv.remove();

    // Show error if URL is empty
    if (!url) {
      const errorDiv = document.createElement("div");
      errorDiv.classList.add("error-msg");
      errorDiv.style.display = "flex";
      errorDiv.style.position = "relative";
      errorDiv.style.alignItems = "center";
      errorDiv.style.padding = "10px 0px";
      errorDiv.style.width = "89%";
      errorDiv.style.margin = "0 auto";
      errorDiv.style.borderRadius = "10px";
      errorDiv.style.overflow = "hidden";
      errorDiv.style.background = "#FAD4D4";
      errorDiv.style.boxShadow = "0 2px 6px rgba(0, 0, 0, 0.1)";
      errorDiv.style.color = "#e03c3cff";
      errorDiv.innerText = "Enter valid URL";

      const form = document.querySelector("#video-container");
      form.appendChild(errorDiv);
      return;
    }

    // Extract YouTube video ID
    const videoIdMatch = url.match(
      /(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|embed\/)|youtu\.be\/)([^\s&?/]+)/i
    );
    if (!videoIdMatch || !videoIdMatch[1]) {
      const errorDiv = document.createElement("div");
      errorDiv.classList.add("error-msg");
      errorDiv.innerText = "Invalid YouTube URL";
      errorDiv.style.display = "flex";
      errorDiv.style.position = "relative";
      errorDiv.style.alignItems = "center";
      errorDiv.style.padding = "10px 0px";
      errorDiv.style.width = "89%";
      errorDiv.style.margin = "0 auto";
      errorDiv.style.borderRadius = "10px";
      errorDiv.style.overflow = "hidden";
      errorDiv.style.background = "#FAD4D4";
      errorDiv.style.boxShadow = "0 2px 6px rgba(0, 0, 0, 0.1)";
      errorDiv.style.color = "#e03c3cff";

      const form = document.querySelector("#video-container");
      form.appendChild(errorDiv);
      return;
    }

    const videoId = videoIdMatch[1];
    const apiUrl = `https://noembed.com/embed?url=https://www.youtube.com/watch?v=${videoId}`;

    fetch(apiUrl)
      .then((res) => res.json())
      .then((data) => {
        const container = document.querySelector("#video-container");

        const newDiv = document.createElement("div");
        newDiv.classList.add("title-div");
        newDiv.style.boxShadow = "inset 0 4px 8px rgba(0,0,0,0.25)";
        newDiv.style.backgroundColor = "white";
        newDiv.style.borderRadius = "10px";
        newDiv.style.marginTop = "10px";
        newDiv.style.padding = "10px";
        newDiv.style.textAlign = "center";

        const title = document.createElement("h3");
        title.innerText = data.title || "No Title Found";

        const thumbnail = document.createElement("img");
        thumbnail.src = `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;
        thumbnail.style.width = "100%";
        thumbnail.style.maxWidth = "320px";
        thumbnail.style.borderRadius = "10px";
        thumbnail.style.marginTop = "10px";

        newDiv.appendChild(title);
        newDiv.appendChild(thumbnail);
        container.appendChild(newDiv);

        const quality = document.createElement("div");
        quality.style.borderRadius = "6px";
        quality.style.textAlign = "center";
        quality.style.margin = "20px";
        quality.style.padding = "20px";
        quality.style.background = "#C4E1E6";
        quality.style.boxShadow =
          "rgba(0, 0, 0, 0.05) 0px 6px 24px 0px, rgba(0, 0, 0, 0.08) 0px 0px 0px 1px";

        const form = document.createElement("form");
        form.method = "POST";
        form.action = "/download";

        const urlInputHidden = document.createElement("input");
        urlInputHidden.type = "hidden";
        urlInputHidden.name = "url";
        urlInputHidden.value = `https://www.youtube.com/watch?v=${videoId}`;
        form.appendChild(urlInputHidden);

     // Map each quality to its YouTube itag
const qualityMap = {
  "360p": "18",
  "480p": "135",
  "720p": "22",
  "1080p": "137",
  "1440p": "264"
};

const qualities = ["360p", "480p", "720p", "1080p", "1440p"];
qualities.forEach((q) => {
  const btn = document.createElement("button");
  btn.type = "submit";
  btn.name = "itag";  // <-- THIS is the fix
  btn.value = qualityMap[q]; // <-- Send itag, not resolution string
  btn.innerText = q;

  btn.style.border = "1px solid #1750a0";
  btn.style.borderRadius = "7px";
  btn.style.padding = "10px";
  btn.style.color = "#1750a0";
  btn.style.background = "white";
  btn.style.width = "15%";
  btn.style.margin = "5px";

  btn.addEventListener("mouseover", () => {
    btn.style.backgroundColor = "#1750a0";
    btn.style.color = "white";
    btn.style.cursor = "pointer";
  });

  btn.addEventListener("mouseout", () => {
    btn.style.background = "white";
    btn.style.color = "#1750a0";
  });

  form.appendChild(btn);
});


        quality.appendChild(form);
        newDiv.appendChild(quality);
      })
      .catch((err) => {
        const container = document.querySelector("#video-container");
        const errorDiv = document.createElement("div");
        errorDiv.classList.add("error-msg");
        errorDiv.innerText = "Could not fetch video details.";
        container.appendChild(errorDiv);
      });
  });
});
