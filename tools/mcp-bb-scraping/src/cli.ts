import { run } from "./index";

run(process.argv.slice(2)).catch((error) => {
  process.stderr.write(String(error) + "\n");
  process.exitCode = 1;
});
