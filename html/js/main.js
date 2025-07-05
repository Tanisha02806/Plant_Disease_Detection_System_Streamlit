//Homepage

// Smooth scroll to the section when "OUR SERVICES" is clicked
document.querySelector('.services-header a').addEventListener('click', function (e) {
    e.preventDefault();
    document.querySelector('#services-header').scrollIntoView({ behavior: 'smooth' });
});

// Fade-in animation for cards on scroll
const cards = document.querySelectorAll('.card');

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in');
        }
    });
}, { threshold: 0.3 });

cards.forEach(card => {
    observer.observe(card);
});

