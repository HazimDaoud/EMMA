// Alert box design by Igor Ferrão de Souza: https://www.linkedin.com/in/igor-ferr%C3%A3o-de-souza-4122407b/

const cuteAlert = ({
                       url,
                       type,
                       title,
                       message,
                       img,
                       buttonText = 'OK',
                       confirmText = 'OK',
                       vibrate = [],
                       playSound = null,
                       cancelText = 'Cancel',
                       closeStyle,
                   }) => {
    return new Promise(resolve => {
        const existingAlert = document.querySelector('.alert-wrapper');

        if (existingAlert) {
            existingAlert.remove();
        }

        const body = document.querySelector('body');

        const scripts = document.getElementsByTagName('script');

        let src = '';

        for (let script of scripts) {
            if (script.src.includes('alert.js')) {
                src = script.src.substring(0, script.src.lastIndexOf('/'));
            }
        }

        let btnTemplate = `
    <button class="alert-button ${type}-bg ${type}-btn" id="alert-btn">${buttonText}</button>
    `;

        if (type === 'question') {
            btnTemplate = `
      <div class="question-buttons">
        <button class="confirm-button ${type}-bg ${type}-btn">${confirmText}</button>
        <button class="cancel-button error-bg error-btn">${cancelText}</button>
      </div>
      `;
        }

        if (vibrate.length > 0) {
            navigator.vibrate(vibrate);
        }

        if (playSound !== null) {
            let sound = new Audio(playSound);
            sound.play();
        }

        const template = `
    <div class="alert-wrapper">
      <div class="alert-frame">
        ${
            img === undefined
                ? '<div class="alert-header ' + type + '-bg">'
                : '<div class="alert-header-base">'
        }
          ${
            img === undefined
                ? '<img class="alert-img" src="' +
                "/static/images/" +
                type +
                ".svg" +
                '" />'
                : '<div class="custom-img-wrapper">' + img + "</div>"
        }
        </div>
        <div class="alert-body">
          <span class="alert-title">${title}</span>
          <span class="alert-message">${message}</span>
          ${btnTemplate}
        </div>
      </div>
    </div>
    `;

        body.insertAdjacentHTML('afterend', template);

        const alertWrapper = document.querySelector('.alert-wrapper');
        const alertFrame = document.querySelector('.alert-frame');
        const alertClose = document.querySelector('.alert-close');
        setTimeout(() => {
            alertWrapper.classList.add('show')
        }, 1);

        if (type === 'question') {
            const confirmButton = document.querySelector('.confirm-button');
            const cancelButton = document.querySelector('.cancel-button');

            confirmButton.addEventListener('click', () => {
                alertWrapper.remove();
                resolve('confirm');
            });

            cancelButton.addEventListener('click', () => {
                alertWrapper.remove();
                resolve();
            });
        } else {
            const alertButton = document.querySelector('.alert-button');

            alertButton.addEventListener('click', () => {
                freeze = false
                alertWrapper.classList.remove('show'); // Add the close class to initiate the close animation
                setTimeout(() => {
                    alertWrapper.remove(); // Remove the alert-wrapper after the animation
                    resolve('ok');
                }, 301); // Adjust the timeout to match the close-popup animation duration (0.3s)
            });
        }

        alertClose.addEventListener('click', () => {
            alertWrapper.remove();
            resolve('close');
        });

        /*     alertWrapper.addEventListener('click', () => {
              alertWrapper.remove();
              resolve();
            }); */

        alertFrame.addEventListener('click', e => {
            e.stopPropagation();
        });
    });
};
