$(function() {
    // jQuery reverse
    $.fn.reverse = [].reverse;
    // Hover behaviour: make sure this doesn't work on .click-to-toggle FABs!
    $(document).on('mouseenter.fixedActionBtn', '.fixed-action-btn', function(e) {
        var $this = $(this);
        $(".fa-arrow-left").fadeIn();
        $(".fa-paper-plane").hide();
        // $("#mainFloat i").addClass("fa-spin");
        openFABMenu($this);
    });
    // this is set of above mouseenter function
    $(document).on('mouseleave.fixedActionBtn', '.fixed-action-btn', function(e) {
        var $this = $(this);
        $(".fa-paper-plane").fadeIn();
        $(".fa-arrow-left").hide();
        closeFABMenu($this);
    });

    // king size floating button with plain icon
    $(document).on('click.mainFloatBtn', '#mainFloat', function(e) {
        toggleChat();
    });

    // floating private list button
    $(document).on('click.fixedActionSubBtn', '#private', function(e) {
        privateList();
    });

    // floating random button
    $(document).on('click.fixedActionSubBtn', '#random', function(e) {
        randomChat();
    });

    // joining room button
    $(document).on('click.profileEnterBtn', '.join-room-btn', function(e) {
        var $this = $(this);
        enterChat($this);
        openChat();
    });
});

var openFABMenu = function(btn) {
    var $this = btn;
    if ($this.hasClass('active') === false) {

      // Get direction option
      var horizontal = $this.hasClass('horizontal');
      var offsetY, offsetX;

      if (horizontal === true) {
        offsetX = 40;
      } else {
        offsetY = 40;
      }

      $this.addClass('active');
      $this.find('ul .btn-floating').velocity(
        { scaleY: ".4", scaleX: ".4", translateY: offsetY + 'px', translateX: offsetX + 'px'},
        { duration: 0 });

      var time = 0;
      $this.find('ul .btn-floating').reverse().each( function () {
        $(this).velocity(
          { opacity: "1", scaleX: "1", scaleY: "1", translateY: "0", translateX: '0'},
          { duration: 80, delay: time });
        time += 40;
      });
    }
};

var closeFABMenu = function(btn) {
    var $this = btn;
    // Get direction option
    var horizontal = $this.hasClass('horizontal');
    var offsetY, offsetX;

    if (horizontal === true) {
      offsetX = 40;
    } else {
      offsetY = 40;
    }

    $this.removeClass('active');
    var time = 0;
    $this.find('ul .btn-floating').velocity("stop", true);
    $this.find('ul .btn-floating').velocity(
      { opacity: "0", scaleX: ".4", scaleY: ".4", translateY: offsetY + 'px', translateX: offsetX + 'px'},
      { duration: 80 }
    );
};

var toggleChat = function() {
    // $("#floatWindow").fadeToggle();
    if($("#floatWindow").css("display") == "none"){
		$("#floatWindow").fadeIn();
        if($(".chat-body").attr("id")) {
            socket.send(JSON.stringify({
                "command": "join",
                "room": $(".chat-body").attr("id")
            }));
            console.log('join');
        }
	} else {
		$("#floatWindow").fadeOut();
        if($(".chat-body").attr("id")) {
            socket.send(JSON.stringify({
                "command": "leave",
                "room": $(".chat-body").attr("id")
            }));
            console.log('exit');
        }
	}
};

var randomChat = function() {
    var randomID = Math.floor((Math.random() * 995) + 1);
    if (!currentUser){
        //login required
        console.log("please login");
        window.location = URL + 'users/login';
        return;
    } else if ($(".chat-body").attr("id") == randomID) {
        randomID = Math.floor(randomID/2) + 1;
        socket.send(JSON.stringify({
            "command": "leave",
            "room": $(".chat-body").attr("id")
        }));
        socket.send(JSON.stringify({
            "command": "join",
            "room": randomID
        }));
    } else if ($(".chat-body[id]").length) {
        socket.send(JSON.stringify({
            "command": "leave",
            "room": $(".chat-body").attr("id")
        }));
        socket.send(JSON.stringify({
            "command": "join",
            "room": randomID
        }));
    } else {
        // Join room
        socket.send(JSON.stringify({
            "command": "join",
            "room": randomID
        }));
    }
    openChat();
}

var enterChat = function(btn) {
    var $this = btn;
    var type, room;

    [type, room] = $this.attr("id").split("-");
    if(type == 'private') {
        var unread = parseInt($("#unread-" + room).text());
        if(isNaN(unread))
            unread = 0;
        alert_count -= unread;
        if (alert_count <= 0) {
            alert_count = 0;
            $("#alertCounter").css("display","none")
        } else
            $("#alertCounter").css("display","block")
        $("#alertCounter p").text(alert_count)
    }
    if (!currentUser){
        //login required
        console.log("please login");
        window.location = URL + 'users/login';
        return;
    } else if ($(".chat-body").attr("id") == room) {
        console.log('nothing');
    } else if ($(".chat-body[id]").length) {
        socket.send(JSON.stringify({
            "command": "leave",
            "room": $(".chat-body").attr("id")
        }));
        socket.send(JSON.stringify({
            "command": "join",
            "room": room
        }));
    } else {
        // Join room
        socket.send(JSON.stringify({
            "command": "join",
            "room": room
        }));
    }
    openChat();
}

var privateList = function() {
    if (!currentUser){
        //login required
        console.log("please login");
        window.location = URL + 'users/login';
        return;
    } else if ($("#roomList").css("display") != "none") {
        return
    } else {
        $.ajax({
            url: "/private-room-list/",
            type: "POST",
            // data: {
            //     "user": currentUser
            // },
            // handle a successful response
            success: function(result) {
                var table = $(".list-table");
                var tbody = $("<tbody></tbody>");

                for (var i = 0; i < result.room.length; i++){
                    var tr = $("<tr></tr>")
                    var name;

                    name = "<td>";
                    if ( result.room[i].unread_count > 0) {
                        name += " <div class='unread-count orangered' id='unread-" + result.room[i].id + ">"
                            + result.room[i].unread_count + "</div>";
                    }
                    name += result.room[i].name + "</td>"

                    tr.append(name);
                    tr.append("<td style='text-align:right;padding-right:20px;'>"
                        + "<button class='join-room-btn' id='private-" + result.room[i].id + "' style='padding:0 30px;'>enter</button></td>");
                    // tr.append("<td><i class='fa fa-remove '></i></td>");

                    tbody.append(tr);
                    table.append(tbody);
                }
            },
            error: function(e) {
                console.log(e);
            }
        })
    }
    openList();
}

var openChat = function() {
    if($("#noRoomSelected").css("display") != "none") {
        $("#floatWindow").css({
            "width": "500",
            "height": "700",
        });
        $("#noRoomSelected").css("display", "none");
    }
    $("#roomList").css("display", "none");
    $("#chatbox").css("display", "block");

    $(".list-table").children().remove();

    $("#floatWindow").fadeIn();
}

var openList = function() {
    if($("#noRoomSelected").css("display") != "none") {
        $("#floatWindow").css({
            "width": "500",
            "height": "700",
        });
        $("#noRoomSelected").css("display", "none");
    }
    $("#chatbox").css("display", "none");
    $("#roomList").css("display", "block");

    if($(".chat-body").attr("id")) {
        socket.send(JSON.stringify({
            "command": "leave",
            "room": $(".chat-body").attr("id")
        }));
        console.log('exit');
        $(".chat-body").attr("id","")
    }
    $("#floatWindow").fadeIn();
}
