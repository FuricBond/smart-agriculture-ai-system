/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./src/**/*.{js,jsx,ts,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                brand: {
                    50: '#F1F8E9',
                    100: '#DCEDC8',
                    200: '#C5E1A5',
                    300: '#AED581',
                    400: '#66BB6A', // Rice Field Green
                    500: '#4CAF50', // Fresh Crop Green
                    600: '#43A047',
                    700: '#388E3C',
                    800: '#2E7D32', // Deep Leaf Green
                    900: '#1B5E20',
                },
                soil: {
                    100: '#D7CCC8', // Earth Sand
                    200: '#BCAAA4',
                    300: '#A1887F',
                    400: '#8D6E63', // Organic Clay
                    500: '#795548',
                    600: '#6D4C41', // Soil Brown
                    700: '#5D4037',
                    800: '#4E342E',
                    900: '#3E2723',
                },
                harvest: {
                    400: '#FFC107', // Harvest Yellow
                    500: '#FFB300'
                }
            },
            fontFamily: {
                sans: ['Open Sans', 'sans-serif'],
                heading: ['Poppins', 'sans-serif'],
            }
        },
    },
    plugins: [],
}
