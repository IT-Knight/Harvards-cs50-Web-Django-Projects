document.addEventListener('DOMContentLoaded', function() {

    // Use buttons to toggle between views
    document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
    document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
    document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
    document.querySelector('#compose').addEventListener('click', compose_email);
    // // Send Mail
    // document.querySelector('.mail_block').addEventListener('click', (event) => {
    //
    //     });

    // By default, load the inbox
    load_mailbox('inbox');
    });

function compose_email() {

    // Show compose view and hide other views
    document.querySelector('#mailbox-title').style.display = 'none';
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#email-view').innerHTML = '';
    document.querySelector('#compose-view').style.display = 'block';

    // Clear out composition fields
    document.querySelector('#compose-recipients').value = '';
    document.querySelector('#compose-subject').value = '';
    document.querySelector('#compose-body').value = '';
}

// <input onclick="send_mail()" type="submit"/>
function send_mail() {
    const d = document;
        fetch('/emails', {
            method: 'POST',
            body: JSON.stringify({
                recipients: d.querySelector('#compose-recipients').value,
                subject: d.querySelector('#compose-subject').value,
                body: d.querySelector('#compose-body').value
            })
        })
        .then(response => response.json())
        .then(result => {
            // Print result
            console.log(result)
            if (result.message === "Email sent successfully.") {
                d.querySelector('#compose-recipients').value = '';
                d.querySelector('#compose-subject').value = '';
                d.querySelector('#compose-body').value = '';
                d.querySelector('#status_message > b').innerHTML = result.message;
                d.querySelector('#status_message > b').style.color = 'none';
            } else {
                d.querySelector('#status_message > b').innerHTML = "Error: " + result.error;
                d.querySelector('#status_message > b').style.color = 'red';
            }
        })
        .then(event.preventDefault())
        .then(setTimeout(load_mailbox('sent'), 1500))  //doesn't work
        // I DONT KNOW HOW TO LOAD THE SENT MESSAGE RIGHT AFTER SENDING, nothing work
        return false;
}

function reply(mail_id) {

    fetch(`emails/${mail_id}`)
        .then(response => response.json())
        .then(email => {

            // console.log(email);

            let to = email.sender;
            let subject = email.subject;
            let body = email.body;
            body = `
            
On ${email.timestamp} ${email.sender} wrote: 
${body}`

            compose_email();

            document.querySelector('#compose-recipients').value = to;
            if (!subject.startsWith("RE:")) {
                subject = 'RE: ' + subject;
            }
            document.querySelector('#compose-subject').value = subject;
            document.querySelector('#compose-body').value = body;

        })

    // let body = document.querySelector('#e_body').value;
}

function view_mail(mail_id) {
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#emails-view').innerHTML = '';

    fetch(`emails/${mail_id}`)
    .then(response => response.json())
    .then(email => {
        console.log(email);

        document.querySelector('#email-view').innerHTML = `<u>From</u>: ${email.sender}<br/> 
        <u>To</u>: ${email.recipients}<br/>
        <u>Subject</u>: <b>${email.subject}</b><br/>
        <u>Date</u>: ${email.timestamp}<br/>
        ${email.body}<br/><br/>`;

        let reply_btn = document.createElement('input');
        reply_btn.setAttribute('type', 'button');
        reply_btn.setAttribute('value', 'Reply');
        reply_btn.setAttribute('onclick', `reply(${email.id})`);
        reply_btn.setAttribute('class', `btn btn-primary`);

        // document.querySelector('#email-view').insertBefore(reply_btn);
        document.querySelector('#email-view').append(reply_btn);

        if (email.read === false) {
            fetch(`emails/${mail_id}`, {
                method: 'PUT',
                body: JSON.stringify({
                  read: true
                })
            })
        }
    })
}


function archive_mail (mail_id) {

    document.querySelectorAll('div.mail_block').forEach(function(div) {
        div.setAttribute('onclick', '');
    })

    fetch(`emails/${mail_id}`, {
      method: 'PUT',
      body: JSON.stringify({
          archived: true
      })
    })
    .then(response => console.log('archived', response));

    load_mailbox('inbox');
}


function unarchive_mail (mail_id) {

    document.querySelectorAll('div.mail_block').forEach(function(div) {
        div.setAttribute('onclick', '');
    })

    fetch(`emails/${mail_id}`, {
      method: 'PUT',
      body: JSON.stringify({
          archived: false
      })
    })
    .then(response => console.log('unarchived', response));

    load_mailbox('inbox');
}

function load_mailbox(mailbox) {

    //Clear notification about sent email
    document.querySelector('#status_message > b').innerHTML = '';

    //Clear last mailbox
    document.querySelector('#emails-view').innerHTML = '';
    document.querySelector('#email-view').innerHTML = '';
    // document.querySelectorAll('div.mail_block').style.pointerEvents = 'auto';

    // Show the mailbox and hide other views
    document.querySelector('#emails-view').style.display = 'block';
    document.querySelector('#compose-view').style.display = 'none';

    // Show the mailbox name
    document.querySelector('#mailbox-title').style.display = 'block';
    document.querySelector('#mailbox-title').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;


    fetch(`emails/${mailbox}`)
    .then(response => response.json())
    .then(emails => {
        // console.log(emails);

        // ... do something else with emails ...
        for (let shit_key in emails) {
            let mail = emails[shit_key];

            var div = document.createElement('div');
            div.setAttribute('class', 'mail_block');
            div.setAttribute('data-read', mail.read);
            div.setAttribute('data-archived', mail.archived);
            div.setAttribute('onclick', `view_mail(${mail.id})`);


            switch (mailbox) {
                case 'inbox':
                    div.innerHTML = `From: ${mail.sender}<br/>
                    Subject: ${mail.subject}<br/>
                    Date: ${mail.timestamp}<br/><br/>`;

                    var button1 = document.createElement('input');
                    button1.setAttribute('onclick', `archive_mail(${mail.id})`);
                    button1.setAttribute('type', `button`);
                    button1.setAttribute('value', `Archive`);
                    button1.setAttribute('class', `btn btn-secondary`);

                    div.appendChild(button1);
                    document.querySelector('#emails-view').appendChild(div);

                    // document.querySelector('#emails-view').appendChild(button1);
                    break;

                case 'sent':
                    div.innerHTML = `To: ${mail.recipients}<br/>
                    Subject: ${mail.subject}<br/>
                    Date: ${mail.timestamp}<br/><br/>`;
                    document.querySelector('#emails-view').appendChild(div);
                    break;

                case 'archive':
                    div.innerHTML = `From: ${mail.sender}<br/>
                    Subject: ${mail.subject}<br/>
                    Date: ${mail.timestamp}<br/><br/>`;
                    document.querySelector('#emails-view').appendChild(div);
                    var button2 = document.createElement('input');
                    button2.setAttribute('onclick', `unarchive_mail(${mail.id})`);
                    button2.setAttribute('type', `button`);
                    button2.setAttribute('value', `Unarchive`);
                    button2.setAttribute('class', `btn btn-secondary`);
                    button2.style.position = 'relative';
                    button2.style.zIndex = '1';
                    div.appendChild(button2);
                    document.querySelector('#emails-view').appendChild(div);
                    // document.querySelector('#emails-view').appendChild(button2);
                    break;
            }
        }
    })
}

