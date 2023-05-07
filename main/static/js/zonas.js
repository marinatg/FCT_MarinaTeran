$(document).ready(function() {
  var num_divs = 5; // Cambiar por el número de divs que desees generar
  $.ajax({
    url: "/generar_divs/" + num_divs,
    type: "GET",
    dataType: "json",
    success: function(data) {
      for (var i = 0; i < data.divs.length; i++) {
        var div = $("<div></div>").attr("id", data.divs[i].id).html(data.divs[i].html);
        $("#contenedor-divs").append(div);
      }
      // Agregar función para manejar el clic en los botones
      $("button").click(function() {
        alert("¡Haz clic en un botón!");
        // Agregar aquí la lógica para manejar el clic del botón
      });
    },
    error: function(xhr, errmsg, err) {
      console.log(xhr.status + ": " + xhr.responseText);
    }
  });
});
