

// document.addEventListener('DOMContentLoaded', () => {
//     const d = document;
//
//     d.querySelector('#compose-form').onsubmit = () => {
//
//         const recipient = d.querySelector('compose-recipients').value;
//         const subject = d.querySelector('compose-subject').value;
//         const body = d.querySelector('compose-body').value;
//         console.log(recipient, subject, body);
//
//         fetch('/emails', {
//           method: 'POST',
//           body: JSON.stringify({
//               recipients: recipient,
//               subject: subject,
//               body: body
//           })
//         })
//         .then(response => response.json())
//
//         .then(result => {
//             console.log(result);
//         });
//     }
//
// })

