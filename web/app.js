const CONFIG_URL = './publication.json';

function setUnavailable(article, message) {
  const video = article.querySelector('video');
  const unavailable = article.querySelector('.unavailable');
  if (video) {
    video.removeAttribute('src');
    video.hidden = true;
  }
  if (unavailable) {
    unavailable.textContent = message;
    unavailable.hidden = false;
  }
}

function setVideo(article, record) {
  const video = article.querySelector('video');
  const unavailable = article.querySelector('.unavailable');
  if (!video || !record?.path || record.publish !== true) {
    setUnavailable(article, 'Esta obra no está disponible en esta publicación.');
    return;
  }
  video.src = record.path;
  video.poster = record.poster ?? '';
  video.controls = Boolean(record.controls);
  video.hidden = false;
  if (unavailable) unavailable.hidden = true;
  const start = async () => {
    try {
      await video.play();
    } catch {
      video.controls = true;
    }
  };
  video.addEventListener('canplay', start, { once: true });
}

async function initialise() {
  let publication;
  try {
    const response = await fetch(CONFIG_URL, { cache: 'no-store' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    publication = await response.json();
  } catch {
    document.querySelectorAll('[data-work]').forEach((article) => {
      setUnavailable(article, 'La publicación todavía no contiene un video revisado.');
    });
    return;
  }

  document.querySelectorAll('[data-work]').forEach((article) => {
    const key = article.dataset.work;
    setVideo(article, publication.works?.[key]);
  });

  const note = document.querySelector('[data-release-note]');
  if (note && publication.note) {
    note.textContent = publication.note;
    note.hidden = false;
  }
}

initialise();
