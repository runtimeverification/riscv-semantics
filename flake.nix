{
  description = "kriscv - K tooling for the RISC-V architecture";
  inputs = {
    nixpkgs.url = "nixpkgs/nixos-25.05";
    flake-utils.url = "github:numtide/flake-utils";
    uv2nix.url = "github:pyproject-nix/uv2nix/680e2f8e637bc79b84268949d2f2b2f5e5f1d81c";
    # uv2nix requires a newer version of nixpkgs
    # therefore, we pin uv2nix specifically to a newer version of nixpkgs
    # until we replaced our stale version of nixpkgs with an upstream one as well
    # but also uv2nix requires us to call it with `callPackage`, so we add stuff
    # from the newer nixpkgs to our stale nixpkgs via an overlay
    nixpkgs-unstable.url = "github:NixOS/nixpkgs/nixos-unstable";
    uv2nix.inputs.nixpkgs.follows = "nixpkgs-unstable";
    # uv2nix.inputs.nixpkgs.follows = "nixpkgs";
    pyproject-build-systems.url = "github:pyproject-nix/build-system-pkgs/7dba6dbc73120e15b558754c26024f6c93015dd7";
    pyproject-build-systems = {
      inputs.nixpkgs.follows = "uv2nix/nixpkgs";
      inputs.uv2nix.follows = "uv2nix";
      inputs.pyproject-nix.follows = "uv2nix/pyproject-nix";
    };
    pyproject-nix.follows = "uv2nix/pyproject-nix";
  };
  outputs = { self, nixpkgs, flake-utils, pyproject-nix, pyproject-build-systems, uv2nix, nixpkgs-unstable }:
  let
    pythonVer = "310";
  in flake-utils.lib.eachSystem [
      "x86_64-linux"
      "x86_64-darwin"
      "aarch64-linux"
      "aarch64-darwin"
    ] (system:
    let
      pkgs-unstable = import nixpkgs-unstable {
        inherit system;
      };
      # for uv2nix, remove this once we updated to a newer version of nixpkgs
      staleNixpkgsOverlay = final: prev: {
        inherit (pkgs-unstable) replaceVars;
      };
      # due to the nixpkgs that we use in this flake being outdated, uv is also heavily outdated
      # we can instead use the binary release of uv provided by uv2nix for now
      uvOverlay = final: prev: {
        uv = uv2nix.packages.${final.system}.uv-bin;
      };
      kriscvOverlay = final: prev: {
        kriscv = final.callPackage ./nix/kriscv {
          inherit pyproject-nix pyproject-build-systems uv2nix;
          python = final."python${pythonVer}";
        };
      };
      pkgs = import nixpkgs {
        inherit system;
        overlays = [
          staleNixpkgsOverlay
          uvOverlay
          kriscvOverlay
        ];
      };
      python = pkgs."python${pythonVer}";
    in {
      devShells.default = pkgs.mkShell {
        name = "uv develop shell";
        buildInputs = [
          python
          pkgs.uv
        ];
        env = {
          # prevent uv from managing Python downloads and force use of specific 
          UV_PYTHON_DOWNLOADS = "never";
          UV_PYTHON = python.interpreter;
        };
        shellHook = ''
          unset PYTHONPATH
        '';
      };
      packages = rec {
        inherit (pkgs) kriscv;
        default = kriscv;
      };
    }) // {
      overlays.default = final: prev: {
        inherit (self.packages.${final.system}) kriscv;
      };
    };
}
