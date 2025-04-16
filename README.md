<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->

<a id="readme-top"></a>

<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->

<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![project_license][license-shield]][license-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/Ardnys/quip">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">quip</h3>

  <p align="center">
    application streaming to browser
    <br />
    <a href="https://github.com/Ardnys/quip"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/Ardnys/quip">View Demo</a>
    &middot;
    <a href="https://github.com/Ardnys/quip/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    &middot;
    <a href="https://github.com/Ardnys/quip/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About The Project

Google Meet (or any browser real time meeting platform) doesn't allow application sharing with audio. This has become an annoying limitation for me when I wanted to stream party games to my friends. This project is my odd but interesting solution as if Discord on desktop does not exist (it's blocked).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

- [![Python][Python.org]][Python-url]
- [![aiohttp][aiohttp]][aiohttp-url]
- [![webrtc][webrtc]][webrtc-url]
- [![Alpine.js][alpine.js]][alpine-url]
- [![Tailwind][tailwindcss]][tailwind-url]
- [![Rust][Rust.org]][Rust-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->

## Getting Started

This project is still in development. Everything changes constantly so I can't provide any instructions yet.

### Prerequisites

- Python
- Browser
- probably tailwind too

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/Ardnys/quip.git
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->

## Usage

```sh
  python src/webrtc.py
```

_For more examples, please refer to the [Documentation](https://example.com)_

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ROADMAP -->

## Roadmap

- [x] Integrate application streaming into aiortc
- [x] Stream application to browser with good fidelity and response
- [x] Decent UI and controls
- [ ] Create an interface for application audio (there's a Rust package)
- [ ] Create Python bindings
- [ ] Integrate that into quip
  - [ ] Publish the python package?
  - [ ] git submodules?
- [ ] Integrate my theme colors
- [ ] Create release

See the [open issues](https://github.com/Ardnys/quip/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Top contributors:

<a href="https://github.com/Ardnys/quip/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Ardnys/quip" alt="contrib.rocks image" />
</a>

<!-- LICENSE -->

## License

Distributed under the project_license. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->

## Contact

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->

## Acknowledgments

- aiortc project had great examples to give me a starting point.
- windows-capture project gave me the confidence to start this project.
- the audio capture project is giving me even more confidence to continue this project.
- i will provide links when i have time.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[contributors-shield]: https://img.shields.io/github/contributors/Ardnys/quip.svg?style=for-the-badge
[contributors-url]: https://github.com/Ardnys/quip/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Ardnys/quip.svg?style=for-the-badge
[forks-url]: https://github.com/Ardnys/quip/network/members
[stars-shield]: https://img.shields.io/github/stars/Ardnys/quip.svg?style=for-the-badge
[stars-url]: https://github.com/Ardnys/quip/stargazers
[issues-shield]: https://img.shields.io/github/issues/Ardnys/quip.svg?style=for-the-badge
[issues-url]: https://github.com/Ardnys/quip/issues
[license-shield]: https://img.shields.io/github/license/Ardnys/quip.svg?style=for-the-badge
[license-url]: https://github.com/Ardnys/quip/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/linkedin_username
[product-screenshot]: images/screenshot.png
[Python.org]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=yellow&labelColor=3776AB
[Python-url]: https://python.org/
[aiohttp]: https://img.shields.io/badge/aiohttp-3776AB?style=for-the-badge&logo=aiohttp&logoColor=3776AB&labelColor=white
[aiohttp-url]: https://python.org/
[webrtc]: https://img.shields.io/badge/webrtc-333333?style=for-the-badge&logo=webrtc&logoColor=white&labelColor=red
[webrtc-url]: https://webrtc.org/
[alpine.js]: https://img.shields.io/badge/Alpine.js-8BC0D0?style=for-the-badge&logo=alpinedotjs&logoColor=white
[alpine-url]: https://alpinejs.dev/
[tailwindcss]: https://img.shields.io/badge/TailwindCSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white
[tailwind-url]: https://tailwindcss.com/
[Rust.org]: https://img.shields.io/badge/Rust-000000?style=for-the-badge&logo=rust&logoColor=black&labelColor=white
[Rust-url]: https://www.rust-lang.org/
