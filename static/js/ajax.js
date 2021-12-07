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
    $("#settings").click(gen_changer('/profile/edit'));
    $('#main-brand').click(gen_changer('/'));

    // end  
    });

function custom_load(url, selector, success_function) {
    $.get(url, function(html){
        var doc = $(html);
        $(selector).empty().append(doc.find(selector + ' > *'));
        success_function();
    });
}

function gen_changer(url, selector='#content', fade=true) {
        return function(){
            var push_url = function() {window.history.pushState(null, '', url);};
            $('.tooltip').remove(); // поскольку tooltip остается, если виден в блоке контента
            if (fade) 
            {
                var loading = '<div class="d-flex flex-column justify-content-center"><div class="spinner-border align-self-center" role="status"><span class="visually-hidden">Loading...</span></div></div>'
                $(selector).fadeOut('fast', function() {
                    $(selector).html(loading).fadeIn('fast', function() {
                            custom_load(url, selector, push_url); //function() {
                                //$(selector).fadeOut('fast', function() {$(selector).fadeIn('fast', push_url);});
                            //});
                    });
                });
            }
            else 
            {
                custom_load(url, selector, push_url);
            }
        }
    }

 
PushStream.LOG_LEVEL = 'debug';
var global_stream = new PushStream({
    host: window.location.hostname,
    port: window.location.port,
    modes: "websocket|eventsource|stream"
});
global_stream.onmessage = _handleLikeUpdate;
global_stream.removeAllChannels();
try {
    global_stream.addChannel("likes");
    global_stream.connect();
} catch(e) {alert(e)};

var q_stream = new PushStream({
    host: window.location.hostname,
    port: window.location.port,
    modes: "websocket|eventsource|stream"
});
q_stream.onmessage = _handleNewQuestion;
q_stream.removeAllChannels();
try {
    q_stream.addChannel("questions");
    q_stream.connect();
} catch(e) {alert(e)};


function _handleLikeUpdate(eventMessage) {
    if (eventMessage == '') return;
    vals = $.parseJSON(eventMessage);
    if ('q_id' in vals) {
        selector = '#modal_q_'+vals['q_id'];
    }
    else if ('a_id' in vals) {
        selector = '#modal_a_'+vals['a_id'];
    }
    else return;
    if ($(selector).length <= 0) return;
    if ('q_id' in vals) {
        button = $('[id=like_btn][q_id='+vals['q_id']+']')
    }
    else if ('a_id' in vals) {
        button = $('[id=like_btn][a_id='+vals['a_id']+']')
    }
    else return;
    if (button.length <= 0) return;
    button = $(button[0]);
    var likes_count = vals.likes_count;
    button.attr('data-bs-original-title', likes_count);
    if (button.is('[aria-describedby]'))
    {
        tooltip_id = button.attr('aria-describedby');
        $('#' + tooltip_id + ' > .tooltip-inner').html(likes_count);
    }
    gen_changer(window.location.href, selector, fade=false)();
}

function _handleNewQuestion(eventMessage) {
    if (eventMessage == 'OK' & window.location.pathname == '/') {
        gen_changer(window.location.href, '#content', fade=false)();
    }
}

function _new_question() {
    q_stream.sendMessage('OK');
}

function _update_like(data) {
    global_stream.sendMessage(JSON.stringify(data));
}
  
function like() {
    button = $(this);
    if ($(this).is('[q_id]'))
    {
       data_input = {'q_id': $(this).attr('q_id')};
    }
    else if ($(this).is('[a_id]'))
    {
       data_input = {'a_id': $(this).attr('a_id')};
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
        data: data_input,
        success: function(data){
            dglobal = Object.assign({}, data, data_input);
            _update_like(dglobal);
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

function get_form(e, selector='#content') {
    var action_url = $(this).attr('action');
    var url = window.location.href;
    e.preventDefault();
    $.ajax({
        type: 'get',
        mode: 'same-origin',
        url: action_url,
        data: $(this).serialize(),
        complete: gen_changer(url, selector)
    });
}