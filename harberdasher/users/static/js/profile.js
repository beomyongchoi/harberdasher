$(function () {

  var jcrop_api,
      boundx,
      boundy,
      xsize = 200,
      ysize = 200;

  $("#crop-picture").Jcrop({
    aspectRatio: xsize / ysize,
    onSelect: updateCoords,
    setSelect: [0, 0, 200, 200]
  },function(){
    var bounds = this.getBounds();
    boundx = bounds[0];
    boundy = bounds[1];
    jcrop_api = this;
  });

  function updateCoords(c) {
    $("#x").val(c.x);
    $("#y").val(c.y);
    $("#w").val(c.w);
    $("#h").val(c.h);
  };

  $("#btn-upload-picture").click(function () {
    $("#picture-upload-form input[name='picture']").click();
  });

  $("#picture-upload-form input[name='picture']").change(function () {
    $("#picture-upload-form").submit();
  });

  $(".close").click(function() {
     $("#modal-upload-picture").hide();
 });
});

// (function() {
//     var dialog = document.getElementById('window');
//   document.getElementById('show').onclick = function() {
//     dialog.show();
//   };
//   document.getElementById('exit').onclick = function() {
//     dialog.close();
//   };
// })();


// $(function() {
//     $(document).on('click', '.private-chat', function(e) {
//         var $this = $(this);
//         getPrivate($this);
//         openChat();
//     });
// });

// function getPrivate(btn) {
//     console.log('gashdighi');
//     var $this = btn;
//     var you = $this.attr("id")
//     $.ajax({
//         url: "private/",
//         type: "POST",
//         data: {
//             "you": you,
//         },
//         // handle a successful response
//         success: function(data) {
//             if (!currentUser){
//                 //login required
//                 console.log("please login");
//                 window.location = URL + 'users/login';
//                 return;
//             } else if ($(".chat-body").attr("id") == data.room) {
//                 console.log('nothing');
//             } else if ($(".chat-body[id]").length) {
//                 socket.send(JSON.stringify({
//                     "command": "leave",
//                     "room": $(".chat-body").attr("id")
//                 }));
//                 socket.send(JSON.stringify({
//                     "command": "join",
//                     "room": data.room
//                 }));
//             } else {
//                 // Join room
//                 socket.send(JSON.stringify({
//                     "command": "join",
//                     "room": data.room
//                 }));
//             }
//         },
//         error: function(e) {
//             console.log(e.responseText);
//         }
//     })
// }
