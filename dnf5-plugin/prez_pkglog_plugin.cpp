// SPDX-License-Identifier: MIT
// Minimal libdnf5 plugin that forwards transaction information to prez-pkglog
// NOTE: This is only a scaffold logic will be filled in later.

#include <dnf5/iplugin.hpp>
#include <libdnf5/base/base.hpp>

using namespace dnf5;

namespace {

constexpr const char * PLUGIN_NAME{"prez_pkglog"};
constexpr PluginVersion PLUGIN_VERSION{.major = 0, .minor = 1, .micro = 0};
constexpr PluginAPIVersion REQUIRED_PLUGIN_API_VERSION{.major = 2, .minor = 0};

class PrezPkglogPlugin : public IPlugin {
public:
    using IPlugin::IPlugin;

    PluginAPIVersion get_api_version() const noexcept override { return REQUIRED_PLUGIN_API_VERSION; }
    const char * get_name() const noexcept override { return PLUGIN_NAME; }
    PluginVersion get_version() const noexcept override { return PLUGIN_VERSION; }

    void init() override;      // called after Base is constructed
    void finish() noexcept override {} // cleanup
};

void PrezPkglogPlugin::init() {
    // Hook into Base callbacks when libdnf5 gains Python-callable transaction hooks.
    // For now, just print a debug line so we know the plugin loaded.
    fprintf(stderr, "[prez_pkglog] libdnf5 plugin initialised (no-op scaffold)\n");
}

} // namespace

// ---- C linkage functions ----------------------------------------------------
extern "C" {

PluginAPIVersion dnf5_plugin_get_api_version(void) {
    return REQUIRED_PLUGIN_API_VERSION;
}

const char * dnf5_plugin_get_name(void) {
    return PLUGIN_NAME;
}

PluginVersion dnf5_plugin_get_version(void) {
    return PLUGIN_VERSION;
}

IPlugin * dnf5_plugin_new_instance([[maybe_unused]] ApplicationVersion application_version, dnf5::Context & context) try {
    return new PrezPkglogPlugin(context);
} catch (...) {
    return nullptr;
}

void dnf5_plugin_delete_instance(IPlugin * plugin_object) {
    delete plugin_object;
}

} // extern "C" 