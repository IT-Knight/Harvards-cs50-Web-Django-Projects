document.addEventListener('DOMContentLoaded', function() {

    set_edit_settings();
    stop_empty_post_posting();
    like_settings();

})


function like_settings() {
    document.querySelectorAll('button.like').forEach(button => {
        button.onclick = () => {
            var post_id = button.dataset.post_id;
            // console.log(post_id)
            let to_do;

            if (button.getAttribute('class').includes('tolike')) {
                button.nextElementSibling.innerHTML++;
                to_do = 'like';
                button.setAttribute('class', 'like dislike');
            } else if (button.getAttribute('class').includes('dislike')) {
                button.nextElementSibling.innerHTML--;
                to_do = "dislike";
                button.setAttribute('class', 'like tolike');
            }

            fetch('/like', {
                    method: 'POST',
                    body: JSON.stringify({
                        post_id: post_id,
                        to_do: to_do
                    })
                })
                .then(result => {
                    // Print result
                    console.log(result);
                });
        }
    })
}


function set_edit_settings () {
    var current_post_id_global;
    var prev_post_id;
    var prev_post_body;

    document.querySelectorAll('[value=edit]').forEach(button => {
        button.onclick = () => {
            let current_post_id = button.dataset.post_id;
            current_post_id_global = current_post_id;
            let current_post_body = document.querySelector(`#post_${current_post_id} > span`).innerHTML;  //selector OK

            // if more then 1 edit form opened
            if (document.querySelector('.editing')) {
                document.querySelector(`#post_${prev_post_id} > span`).innerHTML = prev_post_body; //close prev element without changes
                document.querySelector(`#post_${prev_post_id}`).children[4].style.display = 'unset';
            }
            prev_post_id = current_post_id;
            prev_post_body = current_post_body;

            // open new edit textarea
            document.querySelector(`#post_${current_post_id} > span`).innerHTML =
                `<form id="edit_form"><textarea data-current="text_${current_post_id}"  class="form-control editing">${current_post_body}</textarea>
                 <input type="submit" data-post_id="${current_post_id}"  value="Save" class="btn btn-primary"></form>`

            button.style.display = 'none';
        }
    });
    document.addEventListener('submit', (event) => {
        if (Boolean(document.querySelector('#edit_form'))) {
        // document.querySelector('#edit_form').onsubmit = (event) => {
            event.preventDefault();
            let post_id = current_post_id_global;
            let new_body = document.querySelector(`textarea.editing`).value;
            if (new_body === '') {
                window.alert('You cant leave an empty post!')
                return false
            }

            // fetch put - EDIT FORM
            fetch('/edit', {
                method: 'PUT',
                body: JSON.stringify({
                    post_id: post_id,
                    text: new_body,
                    edited: true
                })
            })
                // .then(response => response.json())
                .then(result => {
                    // Print result
                    console.log(result);
                });

            document.querySelector(`#post_${post_id} > span`).innerHTML = new_body;
            document.querySelector(`#post_${prev_post_id}`).children[4].style.display = 'unset';
            }
            // return false;
    })
}

function stop_empty_post_posting() {
    if (Boolean(document.querySelector('#post-form'))) {
        document.querySelector('#post-form').onsubmit = () => {
            if (document.querySelector('#post_textarea').value === '') {
                window.alert('You cant post an empty post!')
                return false
            }
        }
    }
}





