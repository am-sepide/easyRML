$(document).on("change", "#uploadttlfile", function () {
  event.preventDefault();
  var form_data = new FormData($("#formttl")[0]);
  // $("#formttl").submit();

  $.ajax({
    type: "POST",
    url: "/readOntology",
    data: form_data,
    contentType: false,
    cache: false,
    processData: false,
    async: false,
    success: function (data) {
      alert(data);
      $.ajax({
        url:'/suggestClass',
        type:'GET',
        contentType: "application/json",
        dataType: 'json',
          success: function( json ) {
            $.each(json, function(file) {
                $('#selectclass').append($('<option value="' + this + '">' + this + '</option>'));
              });
            }
          });
    },
    error: function (jqXHR, textStatus, errorThrown) {
      console.log(jqXHR);
      console.log(textStatus);
      console.log(errorThrown);
    },
  });

  return false;
});
