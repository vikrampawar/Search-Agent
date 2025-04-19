# COPILOT Journal

## 2025-04-18
- Added responsive support to `index.html`:
  - Inserted `<meta name="viewport" content="width=device-width, initial-scale=1.0">` in the `<head>` to enable proper scaling on mobile devices.
  - Created a CSS media query targeting screens up to 600px wide to adjust layout and typography:
    - Reduced `body` padding.
    - Scaled down `<h1>` font size and spacing.
    - Shortened `#messages` container height.
    - Switched the form layout to vertical stacking.
    - Adjusted input field margins and font size.
    - Made the send button span full width.
    - Allowed chat messages (`.message`) to utilize full available width.

## 2025-04-19
- Added a new section to `README.md` for deploying with Terraform, including prerequisites, quick start, and troubleshooting steps.
- Updated all SSH commands in the README to use the actual key and EC2 instance values (`~/keys/vikramitwork-ec2-001-rsa.pem` and `ec2-user@35.176.72.243`).
- Ensured both manual and Terraform deployment instructions are available and clearly separated for user reference.