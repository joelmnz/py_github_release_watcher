# GitHub Release Notes Watcher

This is a client-side web application that allows you to watch and display the latest release notes from multiple GitHub repositories.

## Features

- Watch multiple GitHub repositories
- Display latest release notes for each watched repository
- Sort releases by date
- Persist watched repositories and cached data in browser's localStorage
- Markdown rendering of release notes

## Usage

1. Clone this repository or download the `index.html` file.
2. Open `index.html` in a web browser.
3. Click on "Settings" to add repositories you want to watch (format: owner/repo, one per line).
4. Click "Save" to save your settings.
5. Click "Check for Updates" to fetch the latest release notes.

## Deployment

This application can be easily deployed using GitHub Pages:

1. Fork this repository or create a new one and add the `index.html` file.
2. Go to your repository settings on GitHub.
3. Navigate to the "Pages" section.
4. Under "Source", select the branch containing your `index.html` file (usually `main`).
5. Click "Save".

Your application will now be available at `https://your-username.github.io/your-repo-name/`.

## Development

To make changes to the application:

1. Edit the `index.html` file.
2. Test locally by opening the file in a web browser.
3. Commit and push your changes to GitHub if you're using GitHub Pages for deployment.

## Limitations

- This application uses the GitHub API without authentication, so it's subject to rate limiting.
- It can only access public repositories and information.
- All data is stored locally in the user's browser.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).
