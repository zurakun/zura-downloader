// File: static/script.js (Versi Aman)

async function getVideoInfo() {
  const urlInput = document.getElementById("url");
  const status = document.getElementById("status");
  const mainButton = document.getElementById("main-button");
  const downloadOptions = document.getElementById("download-options");

  if (!urlInput.value) {
    status.innerText = "URL tidak boleh kosong!";
    return;
  }

  // Menggunakan status teks biasa untuk loading
  status.innerText = "Mencari pilihan format...";
  downloadOptions.classList.add("hidden");
  mainButton.disabled = true;

  try {
    const response = await fetch("/getinfo", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: urlInput.value }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Gagal mengambil info video.');
    }

    const data = await response.json();
    status.innerText = `Ditemukan: "${data.title}"`;

    const resolutionSelect = document.getElementById("resolution-select");
    const downloadMp4Btn = document.getElementById("download-mp4-btn");
    const downloadMp3Btn = document.getElementById("download-mp3-btn");
    
    // Atur Opsi MP4 (Video)
    resolutionSelect.innerHTML = "";
    if (data.video_formats && data.video_formats.length > 0) {
      data.video_formats.sort((a, b) => parseInt(b.resolution) - parseInt(a.resolution));
      data.video_formats.forEach(format => {
        const option = document.createElement("option");
        option.value = format.format_id;
        option.innerText = `${format.resolution} (${format.filesize_human})`;
        resolutionSelect.appendChild(option);
      });
      downloadMp4Btn.onclick = () => {
        const formatId = resolutionSelect.value;
        window.location.href = `/download?url=${encodeURIComponent(urlInput.value)}&format_id=${formatId}&type=video`;
      };
      resolutionSelect.disabled = false;
      downloadMp4Btn.disabled = false;
    } else {
      resolutionSelect.disabled = true;
      downloadMp4Btn.disabled = true;
    }
    
    // Atur Opsi MP3 (Audio) - Sekarang selalu aktif
    downloadMp3Btn.disabled = false;
    downloadMp3Btn.onclick = () => {
      window.location.href = `/download?url=${encodeURIComponent(urlInput.value)}&type=audio`;
    };

    downloadOptions.classList.remove("hidden");

  } catch (err) {
    status.innerText = "Terjadi kesalahan: " + err.message;
  } finally {
    mainButton.disabled = false;
  }
}

// Atur tahun copyright secara dinamis
document.addEventListener('DOMContentLoaded', function() {
  document.getElementById('copyright-year').textContent = new Date().getFullYear();
});