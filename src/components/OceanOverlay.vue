<template>
    <div class="ocean-overlay">
        <svg class="compass-rose" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <radialGradient id="compassGrad" cx="50%" cy="50%" r="50%">
                    <stop offset="0%" stop-color="#ffffff" stop-opacity="1"/>
                    <stop offset="100%" stop-color="#cccccc" stop-opacity="1"/>
                </radialGradient>
            </defs>

            <circle cx="100" cy="100" r="92" fill="none" stroke="#ffffff" stroke-width="1.2" opacity="0.7"/>
            <circle cx="100" cy="100" r="86" fill="none" stroke="#ffffff" stroke-width="0.5" opacity="0.5"/>

            <g stroke="#ffffff" stroke-width="0.8" opacity="0.6">
                <line x1="100" y1="10" x2="100" y2="18"/>
                <line x1="100" y1="182" x2="100" y2="190"/>
                <line x1="10" y1="100" x2="18" y2="100"/>
                <line x1="182" y1="100" x2="190" y2="100"/>
                <line x1="35" y1="35" x2="41" y2="41"/>
                <line x1="159" y1="35" x2="153" y2="41"/>
                <line x1="35" y1="165" x2="41" y2="159"/>
                <line x1="159" y1="165" x2="153" y2="159"/>
                <line x1="57" y1="14.6" x2="59.5" y2="20.2"/>
                <line x1="143" y1="14.6" x2="140.5" y2="20.2"/>
                <line x1="57" y1="185.4" x2="59.5" y2="179.8"/>
                <line x1="143" y1="185.4" x2="140.5" y2="179.8"/>
                <line x1="14.6" y1="57" x2="20.2" y2="59.5"/>
                <line x1="14.6" y1="143" x2="20.2" y2="140.5"/>
                <line x1="185.4" y1="57" x2="179.8" y2="59.5"/>
                <line x1="185.4" y1="143" x2="179.8" y2="140.5"/>
            </g>

            <polygon points="100,22 96,100 100,88 104,100" fill="#ffffff" opacity="0.9"/>
            <polygon points="100,178 96,100 100,112 104,100" fill="#cccccc" stroke="#ffffff" stroke-width="0.6" opacity="0.9"/>
            <polygon points="178,100 100,96 112,100 100,104" fill="#ffffff" opacity="0.9"/>
            <polygon points="22,100 100,96 88,100 100,104" fill="#cccccc" stroke="#ffffff" stroke-width="0.6" opacity="0.9"/>

            <polygon points="153,47 100,96 106,106 104,96" fill="#ffffff" opacity="0.75"/>
            <polygon points="47,153 100,104 94,94 96,104" fill="#cccccc" stroke="#ffffff" stroke-width="0.5" opacity="0.75"/>
            <polygon points="47,47 100,96 96,106 94,96" fill="#ffffff" opacity="0.75"/>
            <polygon points="153,153 100,104 104,94 106,104" fill="#cccccc" stroke="#ffffff" stroke-width="0.5" opacity="0.75"/>

            <circle cx="100" cy="100" r="12" fill="url(#compassGrad)" stroke="#ffffff" stroke-width="1.2"/>
            <circle cx="100" cy="100" r="4" fill="#ffffff" opacity="0.8"/>

            <text x="100" y="9" text-anchor="middle" font-size="10" font-family="Georgia, serif" font-weight="bold" fill="#ffffff" letter-spacing="1">N</text>
            <text x="100" y="198" text-anchor="middle" font-size="8" font-family="Georgia, serif" fill="#ffffff" opacity="0.7">S</text>
            <text x="196" y="104" text-anchor="middle" font-size="8" font-family="Georgia, serif" fill="#ffffff" opacity="0.7">E</text>
            <text x="4" y="104" text-anchor="middle" font-size="8" font-family="Georgia, serif" fill="#ffffff" opacity="0.7">W</text>

            <g transform="translate(100, 20) scale(0.55)" fill="#ffffff" opacity="0.85">
                <path d="M0,-14 C-2,-10 -5,-8 -5,-4 C-5,0 -2,1 0,1 C2,1 5,0 5,-4 C5,-8 2,-10 0,-14Z"/>
                <path d="M0,1 C-4,0 -7,2 -6,5 C-5,8 -2,7 0,7 C2,7 5,8 6,5 C7,2 4,0 0,1Z"/>
                <path d="M-5,-4 C-9,-6 -12,-4 -11,-1 C-10,2 -7,1 -5,1"/>
                <path d="M5,-4 C9,-6 12,-4 11,-1 C10,2 7,1 5,1"/>
                <rect x="-1" y="7" width="2" height="5" rx="1"/>
            </g>
        </svg>
    </div>
</template>


