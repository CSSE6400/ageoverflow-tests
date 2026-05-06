import encoding from "k6/encoding";
import { randomIntBetween } from "https://jslib.k6.io/k6-utils/1.2.0/index.js";

// k6 doesn't support lorem ipsum generation, so we implement a simple one here for filler text in photos.
// https://www.geeksforgeeks.org/javascript/create-your-own-lorem-ipsum-using-html-css-and-javascript/
function loremGenerator(numWords) {
  // Lorem Ipsum text for demonstration purposes
  const loremIpsumText = `Lorem ipsum dolor sit amet, consectetur 
        adipiscing elit, sed do eiusmod tempor 
        incididunt ut labore et dolore magna 
        aliqua. Diam in arcu cursus euismod 
        quis viverra nibh. Nunc aliquet bibendum
        enim facilisis gravida neque convallis 
        a cras. Sagittis purus sit amet volutpat
        Consequat mauris. Duis ultricies lacus 
        sed turpis tincidunt id.`;

  // Split the Lorem Ipsum text into words
  const words = loremIpsumText.split(" ");

  // Ensure the number of words requested is
  // within the bounds of the available words
  if (numWords <= words.length) {
    return words.slice(0, numWords).join(" ");
  } else {
    return words.join(" ");
  }
}

export class Photo {
  constructor(
    complexity = 8,
    age = 29,
    silent = 0,
    boomer = 0,
    x = 0,
    y = 60,
    z = 40,
    alpha = 0,
    filler = null,
  ) {
    this.complexity = complexity;
    this.age = age;
    this.silent = silent;
    this.boomer = boomer;
    this.x = x;
    this.y = y;
    this.z = z;
    this.alpha = alpha;
    this.filler =
      filler !== null ? filler : loremGenerator(randomIntBetween(15, 35));
  }

  asPayload() {
    let raw = `${this.complexity}|${this.age}|${this.silent}|${this.boomer}|${this.x}|${this.y}|${this.z}|${this.alpha}|${this.filler}`;
    return encoding.b64encode(raw);
  }

  checksum() {
    return "0x" + this.age.toString(16);
  }
}

export function normalPhoto(complexity) {
  let age = randomIntBetween(18, 80);
  return new Photo(complexity, age);
}

export function getPhotos(generator) {
  let complexity, count;

  switch (generator) {
    case "quick":
      complexity = 8;
      count = 1;
      break;
    case "heavy":
      complexity = randomIntBetween(13, 20);
      count = 1;
      break;
    case "normal":
    default:
      complexity = randomIntBetween(8, 20);
      count = randomIntBetween(1, 2);
      break;
  }

  let payloads = [];
  let totalAge = 0;
  for (let i = 0; i < count; i++) {
    let photo = normalPhoto(complexity);
    payloads.push(photo.asPayload());
    totalAge += photo.age;
  }

  // Expected processing delay based on engine benchmarks
  let expectedDelay;
  if (complexity <= 10) {
    expectedDelay = 1;
  } else if (complexity <= 12) {
    expectedDelay = 2;
  } else if (complexity <= 16) {
    expectedDelay = 5;
  } else {
    expectedDelay = 18;
  }

  return {
    payloads: payloads,
    checksum: "0x" + totalAge.toString(16),
    expectedDelay: expectedDelay,
  };
}
