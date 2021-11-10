function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$(function(){
    // don't cache ajax or content won't be fresh
    $.ajaxSetup ({
        cache: false
    });

    var ajax_load = ""; //"<div class='container text-center mx-auto'><img src='http://i.imgur.com/pKopwXp.gif' alt='loading...' /></div>";
    
    $("#ask").click(gen_changer('/ask'));
    $("#signup").click(gen_changer('/signup'));
    $("#login").click(gen_changer('/login'));
    $("#settings").click(gen_changer('/settings'));
    $('#main-brand').click(gen_changer('/'));

    // end  
    });

function gen_changer(url, selector='#content', fade=true) {
        return function(){
            var push_url = function() {window.history.pushState(null, '', url);};
            $('.tooltip').remove(); // поскольку tooltip остается, если виден в блоке контента
            if (fade) 
            {
                var loading = '<div class="spinner-border ms-auto me-auto" role="status"><span class="visually-hidden">Loading...</span></div>'
                $(selector).fadeOut('fast', function() {
                    $(selector).html(loading).fadeIn('fast', function() {
                            $(selector).load(url+' '+selector + ' > *', push_url); //function() {
                                //$(selector).fadeOut('fast', function() {$(selector).fadeIn('fast', push_url);});
                            //});
                    });
                });
            }
            else 
            {
                $(selector).load(url+' '+selector + ' > *', push_url);
            }
        }
    }

function like() {
    button = $(this);
    if ($(this).is('[q_id]'))
    {
       data = {'q_id': $(this).attr('q_id')};
    }
    else if ($(this).is('[a_id]'))
    {
       data = {'a_id': $(this).attr('a_id')};
    }
    else
    {
        return;
    }

    $.ajax({
        type: 'post',
        url: '/like',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
          },
        dataType: "json",
        data: data,
        success: function(data){
            button.attr('data-bs-original-title', data.likes_count);
            if (button.is('[aria-describedby]'))
            {
                tooltip_id = button.attr('aria-describedby');
                $('#' + tooltip_id + ' > .tooltip-inner').html(data.likes_count);
            }
        }
    });
};

function set_correct() {
    button = $(this);
    if (button.is('[a_id]'))
    {
        $.ajax({
            type: 'post',
            url: '/set_correct',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            dataType: "json",
            data: {'a_id': button.attr('a_id')},
            complete: function() {
                gen_changer(window.location.href, '#answers_block', false)();
            }
        })
    }
    else
    {
        return;
    }
}

function post_form(e) {
    var action_url = $(this).attr('action');
    var url = window.location.href;
    e.preventDefault();
    $.ajax({
        type: 'post',
        mode: 'same-origin',
        url: action_url,
        data: $(this).serialize(),
        complete: gen_changer(url, '#content')
    });
};