# Project-specific nixvim overrides for without-ai (Python/FastAPI + Next.js frontend)
{pkgs, ...}: {
  plugins = {
    # LSP servers
    lsp.servers = {
      pyright = {
        enable = true;
        package = pkgs.pyright;
      };
      ts_ls = {
        enable = true;
        package = pkgs.typescript-language-server;
      };
      eslint = {
        enable = true;
        package = pkgs.vscode-langservers-extracted;
      };
    };

    # Formatting
    conform-nvim.settings.formatters_by_ft = {
      python = ["ruff_format"];
      javascript = ["prettier"];
      typescript = ["prettier"];
      javascriptreact = ["prettier"];
      typescriptreact = ["prettier"];
    };

    # Linting
    lint.lintersByFt = {
      python = [
        "ruff"
        "mypy"
      ];
      javascript = ["eslint"];
      typescript = ["eslint"];
    };
  };
}
