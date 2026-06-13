{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    git-hooks = {
      url = "github:cachix/git-hooks.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = {
    nixpkgs,
    flake-utils,
    git-hooks,
    ...
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {inherit system;};

      pre-commit-check = git-hooks.lib.${system}.run {
        src = ./.;
        hooks = {
          alejandra.enable = true;
          statix.enable = true;
          deadnix = {
            enable = true;
            excludes = ["hardware-configuration"];
          };
          flake-checker.enable = true;
          ruff.enable = true;
          ruff-format.enable = true;
          mypy = {
            enable = true;
            args = ["--ignore-missing-imports"];
          };
          end-of-file-fixer.enable = true;
          trim-trailing-whitespace.enable = true;
          check-merge-conflicts.enable = true;
        };
      };
    in {
      checks.pre-commit-check = pre-commit-check;
      formatter = let
        inherit (pre-commit-check) config;
        inherit (config) package configFile;
      in
        pkgs.writeShellScriptBin "pre-commit-run" ''
          ${pkgs.lib.getExe package} run --all-files --config ${configFile}
        '';

      devShells.default = pkgs.mkShell {
        shellHook = ''
          # Guard against global core.hooksPath which breaks pre-commit hook installation.
          _global_hooksPath="$(${pkgs.git}/bin/git config --global core.hooksPath 2>/dev/null || true)"
          if [ -n "$_global_hooksPath" ]; then
            echo ""
            echo "WARNING: core.hooksPath is set globally ('$_global_hooksPath')."
            echo "This prevents pre-commit hooks from being installed by the Nix devShell."
            echo "Remove it with: git config --global --unset-all core.hooksPath"
            echo ""
          fi
          unset _global_hooksPath

          ${pre-commit-check.shellHook}

          # Make Playwright's patched browsers (including Firefox) available.
          # These are the Nix-built browsers; they avoid the dynamic downloads
          # that break on NixOS. Keep your Playwright binding version in sync
          # with the nixpkgs `playwright-driver` version.
          export PLAYWRIGHT_BROWSERS_PATH="${pkgs.playwright-driver.browsers}"
          export PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=true
        '';
        buildInputs = with pkgs;
          [
            git
            python313
            uv
            gnumake
            ruff
            alejandra
          ]
          ++ pre-commit-check.enabledPackages;
      };
    });
}
