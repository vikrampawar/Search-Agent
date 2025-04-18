# Responsive Styling Guide for index.html

This guide walks through the changes made to `index.html` to ensure it looks great on both desktop and mobile devices. It assumes you have basic knowledge of HTML and CSS.

## 1. Add the viewport meta tag
In the `<head>` section, include the following tag:
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```
- **Purpose**: Tells the browser to use the device's width as the page width and sets the initial zoom level to 1. Without it, mobile browsers may render the page zoomed out.

## 2. Understand media queries
CSS media queries let you apply styles conditionally based on the device's characteristics (e.g., width). We use a `max-width` query to target small screens.

```css
@media (max-width: 600px) {
  /* styles for screens 600px wide or less */
}
```

## 3. Apply mobile-specific adjustments
Inside your CSS (either in the `<style>` block or an external stylesheet), add rules under a media query:

```css
@media (max-width: 600px) {
  /* 1. Reduce page padding */
  body {
    padding: 10px;
  }
  
  /* 2. Scale down the main heading */
  h1 {
    font-size: 1.5em;
    margin-bottom: 20px;
  }
  
  /* 3. Shorten the chat container */
  #messages {
    height: 300px;
  }
  
  /* 4. Stack form elements vertically */
  #messageForm {
    display: flex;
    flex-direction: column;
  }
  
  /* 5. Tweak the text input */
  #message {
    margin: 0 0 10px 0;
    font-size: 14px;
  }
  
  /* 6. Make the send button full width */
  #sendButton {
    width: 100%;
    padding: 12px;
  }
  
  /* 7. Allow messages to fill available width */
  .message {
    max-width: 100%;
  }
}
```

### Tips for Testing
- **Browser DevTools**: Open the page in Chrome/Firefox, press `F12` (or right-click → Inspect), then toggle the device toolbar (`Ctrl+Shift+M` in Chrome) to simulate different screen sizes.
- **Real Devices**: Whenever possible, test on an actual phone or tablet to catch subtle differences.

## 4. Further Reading
- [MDN: Using the viewport meta tag](https://developer.mozilla.org/docs/Mozilla/Mobile/Viewport_meta_tag)
- [MDN: Media Queries](https://developer.mozilla.org/docs/Web/CSS/Media_Queries/Using_media_queries)

With these steps, your `index.html` will adapt to both large and small screens, improving readability and user experience on mobile devices.