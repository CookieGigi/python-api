{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    git-hooks = {
      url = "github:cachix/git-hooks.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    nixvim = {
      url = "github:nix-community/nixvim";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = {
    nixpkgs,
    flake-utils,
    git-hooks,
    nixvim,
    ...
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {inherit system;};

      projectNvim = nixvim.legacyPackages.${system}.makeNixvim {
        imports = [
          ./nixvim-base.nix
          ./nixvim.nix
        ];
      };

      pre-commit-check = git-hooks.lib.${system}.run {
        src = ./.;
        hooks = {
          alejandra.enable = true;
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
          ${pre-commit-check.shellHook}

          export UV_LINK_MODE=copy
          export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath [pkgs.stdenv.cc.cc.lib]}:$LD_LIBRARY_PATH"
        '';
        buildInputs = with pkgs;
          [
            git
            python313
            uv
            gnumake
            ruff
            alejandra
            pyright
            mypy
            projectNvim
            lnav
            traefik
            mkcert
            stdenv.cc.cc.lib
          ]
          ++ pre-commit-check.enabledPackages;
      };
    });
}
