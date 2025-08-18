/**
 * Test App
 * 
 * @author Forename Surname
 * @version 1.0.0
 * @since 2025-08-18T12-37
 * @see {@link https://github.com/forename-surname}
 * @license MIT
 */

// < ======================================================
// < Imports
// < ======================================================

// import { 
//     thing
// } from "./folder/things.js";

// < ======================================================
// < Declarations
// < ======================================================

/**
 * Application identifier
 * @type {string}
 */
const APP_NAME = 'App Name';

// - ========================
// - Type Declarations
// - ========================

/** @typedef {{ name: string, age: number }} Person */

// < ======================================================
// < Element Queries
// < ======================================================

const page = /** @type {HTMLDivElement} */
    (document.getElementById('page'));

const main = /** @type {HTMLDivElement} */
    (document.getElementById('main'));

// ~ ======================================================
// ~ Entry Point
// ~ ======================================================

// ? Run callback when all resources have loaded
window.addEventListener('load', () => {

    // ! Show test message
    const message = 'testing';
    const div = document.createElement('div');
    Object.assign(div.style, {
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)'
    });
    div.textContent = message;
    document.body.appendChild(div);
    console.log(message);

});