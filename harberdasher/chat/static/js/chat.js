$(function() {
    // When we're using HTTPS, use WSS too.
    // var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    //
    // socket = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/chat" + window.location.pathname);

    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var ws_path = ws_scheme + '://' + window.location.host + "/chat/stream/";
    console.log("Connecting to " + ws_path);
    socket = new ReconnectingWebSocket(ws_path);


    if (alert_count != 0) {
        $("#alertCounter").css("display","block")
        $("#alertCounter p").text(alert_count)
    }

    // alert_count

    socket.onmessage = function(message) {
        // Decode the JSON
        var data = JSON.parse(message.data);

        // Handle alert
        if (data.count) {
            console.log("incoming private message");
            alert_count += 1;
            if (alert_count <= 0) {
                alert_count = 0;
                $("#alertCounter").css("display","none")
            } else
                $("#alertCounter").css("display","block")
            $("#alertCounter p").text(alert_count)

            var room_count = parseInt($("#unread-" + data.count).text());
            room_count += 1;
            $("#unread-" + data.count).text(room_count);
            // Handle joining
        } else if (data.join) {
            console.log("Joining room " + data.join);
            if($(".chat-body").attr("id") != data.join){
                $(".chat-list").children().remove();
                $(".user-list").children().remove();
            }
            $(".chat-body").attr("id", data.join);
            $(".chat-title h5").text(data.title.replace(firstToUpperCase( currentUser ), ""));

            for (var i = 0, entered; entered = data.list[i]; i++) {
                if ($('#' + entered.user).length ||
                    entered.status == 'inactive') {
                    continue;
                }
                var link;
                var list = $(".user-list");
                var li = $("<li></li>");
                link = "<a class='private-chat"
                if ( entered.user == currentUser) {
                    link += " disabled' ";
                } else {
                    link += "' ";
                }
                link += "id='" + entered.user + "'>" + entered.user + "</a>";
                li.append(link);
                list.append(li);
            }

            if ( data.private && currentUser == data.user) {
                for (var i = 0; i < data.private.length; i++) {
                // Message
                    var list = $(".chat-list");
                    var li = $("<li></li>");
                    var replacedMessage = data.private[i].message.split('\n').join('<br />');

                    if (currentUser == data.private[i].user) {
                        li = $("<li class='self'></li>");
                    } else {
                        li.append("<div class='username'>" + data.private[i].user + "</div>");
                    }
                    li.append("<div class='message'>" + replacedMessage + "</div>");
                    li.append("<time class='timestamp'>" + data.private[i].timestamp + "</time>");

                    list.append(li);

                    $(".chat-body").scrollTop($(".chat-list").height());
                }

            }
            // Handle leaving
        } else if (data.leave) {
            console.log("Leaving room " + data.leave);
            $('#' + data.user).remove();
            // Handle getting a message
        } else if (data.message) {
            // Message
            var list = $(".chat-list");
            var li = $("<li></li>");
            var replacedMessage = data.message.split('\n').join('<br />');

            if (currentUser == data.user) {
                li = $("<li class='self'></li>");
            } else {
                li.append("<div class='username'>" + data.user + "</div>");
            }
            li.append("<div class='message'>" + replacedMessage + "</div>");
            li.append("<time class='timestamp'>" + data.timestamp + "</time>");

            list.append(li);

            $(".chat-body").scrollTop($(".chat-list").height());
        } else {
            console.log("Cannot handle message!");
        }
    }

    $("#chatform").on("submit", function(e) {
        var message = {
            command: 'send',
            room: $(".chat-body").attr("id"),
            message: $('#message').val(),
        };
        if (message.message) {
            socket.send(JSON.stringify(message));
            $("#message").val('');
        }
        $( "#message" ).focus();
        console.log('click');
        return false;
    });

    $(document).on('click', '.private-chat', function(e) {
        var $this = $(this);
        getPrivate($this);
    });
});

function onChange() {
    var key = window.event.keyCode;

    // If the user has pressed enter
    if (key === 13) {
        if (window.event.shiftKey) {
            return false;
        };
        var message = {
            command: 'send',
            room: $(".chat-body").attr("id"),
            message: $('#message').val(),
        };
        if (message.message && socket) {
            socket.send(JSON.stringify(message));
            $("#message").val('');
        }
        window.event.preventDefault();
    }
}

function getPrivate(btn) {
    var $this = btn;
    $.ajax({
        url: "/private/",
        type: "POST",
        data: {
            "you": $this.attr("id"),
        },
        // handle a successful response
        success: function(data) {
            if (!currentUser){
                //login required
                console.log("please login");
                window.location = URL + 'users/login';
                return;
            } else if ($(".chat-body").attr("id") == data.room) {
                console.log('nothing');
            } else if ($(".chat-body[id]").length) {
                socket.send(JSON.stringify({
                    "command": "leave",
                    "room": $(".chat-body").attr("id")
                }));
                socket.send(JSON.stringify({
                    "command": "join",
                    "room": data.room
                }));
            } else {
                // Join room
                socket.send(JSON.stringify({
                    "command": "join",
                    "room": data.room
                }));
                openChat();
            }

        },
        error: function(e) {
            console.log(e.responseText);
        }
    })
}

function firstToUpperCase( str ) {
    return str.substr(0, 1).toUpperCase() + str.substr(1);
}
