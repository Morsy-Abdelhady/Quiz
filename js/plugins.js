/*global $*/
$(document).ready(function () {
    "use strict";

    // Start Menu
    $(".sidebar-menu").on("click", function () {
        $("aside").toggleClass("slide");
        $(".aside-responsive").toggleClass("flexible");
    });
    $(".content .menu li").on("click", function () {
        $(this).addClass("active").siblings().removeClass("active");
    });
    $(".content .menu li:first-of-type").on("click", function () {
        $(".config, .configure-result").fadeIn().siblings().fadeOut(0);
        $(".outcomes-result").hide();
    });
    $(".content .menu li:nth-of-type(2)").on("click", function () {
        $(".outcomes, .outcomes-result").fadeIn().siblings().fadeOut(0);
        $(".configure-result").hide();
    });
    $(".content .menu li:nth-of-type(3)").on("click", function () {
        $(".questions").fadeIn().siblings().fadeOut(0);
    });
    (function () {
        function handleStatusChanged() {
            $('.configure form .switch').on('click', function () {
              toggleStatus();   
            });
        }
        function toggleStatus() {
            if ($('.configure form .switch input').is(':checked')) {
                $('.configure form input[type="text"], .configure form input[type="file"], .configure form textarea, .questions .custom-select, .questions .dropdown button, .controls button').removeAttr('disabled');
                $(".image-upload-wrap").css("background", "#fff")
            } else {
                $('.configure form input[type="text"], .configure form input[type="file"],  .configure form textarea, .questions .custom-select, .questions .dropdown button, .controls button').attr('disabled', true);
                $(".image-upload-wrap").css("background", "#e9ecef")
            }   
        }
        handleStatusChanged();
    })();

    // Start Outcomes
    $(".outcomes .selector li").on("click", function () {
        $(this).addClass("slide-down").siblings().removeClass("slide-down");
    });
    $(".outcomes .selector li:first-of-type").on("click", function () {
        $(".outcomes .redirect").slideDown();
        $(".outcomes .paragraph, .outcomes .image-upload-wrap").hide();
    });
    $(".outcomes .selector li:nth-of-type(2)").on("click", function () {
        $(".outcomes .paragraph").slideDown();
        $(".outcomes .redirect, .outcomes .image-upload-wrap").hide();
    });
    $(".outcomes .selector li:nth-of-type(3)").on("click", function () {
        $(".outcomes .image-upload-wrap").slideDown();
        $(".outcomes .redirect, .outcomes .paragraph").hide();
    });

    // Start Configure Preview
    $("input[name='quiz-title']").keyup( function() {
        $(".configure-result .preview-info h3").html($(this).val());
    });
    $("input[name='quiz-desc']").keyup( function() {
        $(".configure-result .preview-info p").html($(this).val());
    });
    $("input[name='button-title']").keyup( function() {
        $(".configure-result .preview-info button").html($(this).val());
    });
    $(function () {
        $(".config .file-upload-input").change(function () {
            if (this.files && this.files[0]) {
                var reader = new FileReader();
                reader.onload = imageIsLoaded;
                reader.readAsDataURL(this.files[0]);
            }
        });
    });
    function imageIsLoaded(e) {
        $('.configure-result .file-upload-image').attr('src', e.target.result);
        $('.configure-result .file-upload-content').show();
    };

    // Start Outcomes Preview
    $(".redirect input").keyup( function() {
        $(".outcomes-result h2 a").html($(this).val());
    });
    $(".paragraph textarea").keyup( function() {
        $(".outcomes-result .lead").html($(this).val());
    });
    $(function () {
        $(".outcomes .file-upload-input").change(function () {
            if (this.files && this.files[0]) {
                var reader = new FileReader();
                reader.onload = imagesIsLoaded;
                reader.readAsDataURL(this.files[0]);
            }
        });
    });
    function imagesIsLoaded(e) {
        $('.outcomes-result .file-upload-image').attr('src', e.target.result);
        $('.outcomes-result .file-upload-content').show();
    };
});
