/*!
    * Start Bootstrap - SB Admin v7.0.7 (https://startbootstrap.com/template/sb-admin)
    * Copyright 2013-2023 Start Bootstrap
    * Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-sb-admin/blob/master/LICENSE)
    */
    // 
// Scripts
// 

window.addEventListener('DOMContentLoaded', event => {

    // Toggle the side navigation
    const sidebarToggle = document.body.querySelector('#sidebarToggle');
    if (sidebarToggle) {
        // Uncomment Below to persist sidebar toggle between refreshes
        // if (localStorage.getItem('sb|sidebar-toggle') === 'true') {
        //     document.body.classList.toggle('sb-sidenav-toggled');
        // }
        sidebarToggle.addEventListener('click', event => {
            event.preventDefault();
            document.body.classList.toggle('sb-sidenav-toggled');
            localStorage.setItem('sb|sidebar-toggle', document.body.classList.contains('sb-sidenav-toggled'));
        });
    }

});

document.addEventListener('DOMContentLoaded', function() {
        // Event listener for privacy policy link
        document.getElementById('privacy-policy-link').addEventListener('click', function(event) {
            event.preventDefault();
            Swal.fire({
                title: 'Privacy Policy',
                html: '<p style="text-align: justify;">We are committed to protecting your privacy. This privacy policy outlines how we collect, use, disclose, and manage your personal information.</p><p style="text-align: justify;">Please note that our service is for educational purposes only, as part of a school project. We do not collect any personally identifiable information.</p>',
                icon: 'info',
                confirmButtonText: 'Close'
            });
        });

        // Event listener for terms & conditions link
        document.getElementById('terms-conditions-link').addEventListener('click', function(event) {
            event.preventDefault();
            Swal.fire({
                title: 'Terms & Conditions',
                html: '<p style="text-align: justify;">By accessing and using our service, you agree to these terms and conditions. This service is provided solely for educational purposes as part of a school project.</p><p style="text-align: justify;">We do not guarantee the accuracy, reliability, or completeness of any information provided through this service.</p><p style="text-align: justify;">You agree not to misuse, modify, or interfere with the service in any way that violates applicable laws or regulations.</p>',
                icon: 'info',
                confirmButtonText: 'Close'
            });
        });
    });


document.querySelectorAll(".nav-link").forEach((link) => {
    if (link.href === window.location.href) {
        link.classList.add("active");
        link.setAttribute("aria-current", "page");
    }
});



