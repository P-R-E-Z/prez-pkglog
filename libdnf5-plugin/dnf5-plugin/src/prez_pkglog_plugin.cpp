// SPDX-License-Identifier: MIT
// libdnf5 plugin that loads for prez-pkglog

#include <dnf5/iplugin.hpp>
#include <iostream>
#include <libdnf5/base/base.hpp>

using namespace dnf5;

namespace {

constexpr const char* PLUGIN_NAME{"prez_pkglog"};
constexpr PluginVersion PLUGIN_VERSION{.major = 0, .minor = 6, .micro = 3};
constexpr PluginAPIVersion REQUIRED_PLUGIN_API_VERSION{.major = 2, .minor = 0};

class PrezPkglogPlugin : public IPlugin {
   public:
    using IPlugin::IPlugin;

    PluginAPIVersion get_api_version() const noexcept override {
        return REQUIRED_PLUGIN_API_VERSION;
    }
    const char* get_name() const noexcept override {
        return PLUGIN_NAME;
    }
    PluginVersion get_version() const noexcept override {
        return PLUGIN_VERSION;
    }

    void init() override;
    void finish() noexcept override {}

    // Required virtual functions from IPlugin interface
    const char* const* get_attributes() const noexcept override {
        return nullptr;
    }
    const char* get_attribute(const char* name) const noexcept override {
        return nullptr;
    }
    std::vector<std::unique_ptr<Command>> create_commands() override {
        return {};
    }
};

void PrezPkglogPlugin::init() {
    std::cerr << "[prez_pkglog] DNF5 plugin initialized (transaction logging via Actions Plugin)"
              << std::endl;
}

}  // namespace

// C linkage functions
extern "C" {

PluginAPIVersion dnf5_plugin_get_api_version(void) {
    return REQUIRED_PLUGIN_API_VERSION;
}

const char* dnf5_plugin_get_name(void) {
    return PLUGIN_NAME;
}

PluginVersion dnf5_plugin_get_version(void) {
    return PLUGIN_VERSION;
}

IPlugin* dnf5_plugin_new_instance([[maybe_unused]] ApplicationVersion application_version,
                                  dnf5::Context& context) try {
    return new PrezPkglogPlugin(context);
} catch (...) {
    return nullptr;
}

void dnf5_plugin_delete_instance(IPlugin* plugin_object) {
    delete plugin_object;
}

}  // extern "C"