for (const btn of document.querySelectorAll('.vote')) {
    btn.addEventListener('click', event => {
      event.currentTarget.classList.toggle('on');
    });
  }