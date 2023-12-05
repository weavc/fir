## Fir - Command line task management

<small>This project is in development & subject to breaking changes.</small>

Configurable command line task management tool inspired by emacs org mode & web based task management tools.

### Features
- Support for multiple profiles allowing the user to easily switch between task lists. 
- Toml configuration files, easy for humans and source control. See: [example](./fir.v1.todo.toml)
- Configurable outputs (& more to come)
- Support for tags, due dates, assigned people, notes and more
- Configurable statuses, with 3 status categories todo, doing, done (on hold category coming soon).

View tasks with `fir ls` to see all ongoing tasks:

![ls](https://raw.githubusercontent.com/weavc/fir/main/.github/screenshots/1143d8c55c079e3e19ecdaf5221eeb68b57c5e73.png)

### Creating/Modifying tasks:

![Adding a new task](https://raw.githubusercontent.com/weavc/fir/main/.github/screenshots/bd79c6bc12c8a755e056e1a1fe85de7dc5e88ca5.png)

### Upcoming features ideas
- Backlog for tasks that don't show in the regular task lists, but exist in the background ready to be pulled forward.
- Forth status category for tasks that are on hold
- Tracking dates for when the work started & finished (based on when they move status groups)
- Better documentation, help commands etc

### Development

```
git clone git@github.com:weavc/fir.git
cd fir
pip3 install poetry
make shell
make install
```
