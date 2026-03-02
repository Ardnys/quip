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

Google Meet (or any browser real time meeting platform) doesn't allow application sharing with audio. This has become an annoying limitation for me when I wanted to stream party games to my friends. I could have just shared the whole screen with audio but then I could not play on my computer. 

Anyway, I wanted to just share **an application with audio** and my genius (which has its own gravity) decided to stream it via a browser tab. I know it was possible and I just wanted it done. This is the result of it. It's... underwhelming considering the efforts went into it.



<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

- [![Python][Python.org]][Python-url]
- [![aiohttp][aiohttp]][aiohttp-url]
- [![webrtc][webrtc]][webrtc-url]
- [![React][React]][React-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->

## Getting Started

### Prerequisites

- Python & uv
- npm
- Browser
- Windows
- Virtual Audio Cable
- Friends

### Installation & Setup

1. Clone the repo
   ```sh
   git clone https://github.com/Ardnys/quip.git
   ```
2. Install a Virtual Audio Device of you liking. I used [VB-Audio](https://vb-audio.com/Cable/). If you know a better one let me know!
3. Change the speaker output of the app you wish to stream to Virtual Audio Device.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


## Usage

Start the backend server.
```sh
  cd backend
  uv sync
  uv run src/webrtc.py
```


_For more examples, please refer to the [Documentation](https://example.com)_

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ROADMAP -->

## Roadmap

- [x] Integrate application streaming into aiortc
- [x] Stream application to browser with good fidelity and response
- [x] Working audio
- [x] Fix threading issues
- [x] Fix start and stop getting called many times
- [x] Separate audio and video start - stops
- [x] Clean up the code
- [ ] Better logging
- [ ] Complete UI Overhaul
  - [ ] Codec selection
  - [x] Window selection 
  - [x] Audio device selection
  - [x] Fullscreen
- [ ] First release
- [ ] Write the sad project story

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
- unfortunately audio capture project wasn't the correct solution. I realized it after working on it for so long. Actually the project isn't even needed in the first place except extremely, unfathomably unique and niche use cases.
- Claude AI for helping me fix issues very quickly and writing almost all of the frontend. 

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
[aiohttp-url]: https://docs.aiohttp.org/en/stable/
[webrtc]: https://img.shields.io/badge/webrtc-333333?style=for-the-badge&logo=webrtc&logoColor=white&labelColor=red
[webrtc-url]: https://webrtc.org/
[React]: https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=61DAFB&labelColor=23272f
[React-url]: https://react.dev/
